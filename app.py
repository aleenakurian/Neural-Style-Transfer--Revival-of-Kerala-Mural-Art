from flask import Flask, render_template, request, jsonify, send_file
import os
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
import torchvision.transforms as transforms
import torch.nn.functional as F
import torchvision.utils as vutils
import copy
#import tqdm
#from diffusers import StableDiffusionPipeline
#import io

app = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/aleen/Desktop/Mainproject/static/uploads/'
OUTPUT_FOLDER = 'C:/Users/aleen/Desktop/Mainproject/static/'

def load_checkpoint(filepath):
    checkpoint = torch.load(filepath)
    model = checkpoint['model']
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    return model

model = load_checkpoint('C:/Users/aleen/Downloads/checkpoint.pth')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
cnn = model.to(device).eval()


imsize = 512 if torch.cuda.is_available() else 128
loader = transforms.Compose([
    transforms.Resize((imsize, imsize)),
    transforms.ToTensor(),
])

def image_loader(image_name):
    image = Image.open(image_name)
    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)

class ContentLoss(nn.Module):

    def __init__(self, target,):
        super(ContentLoss, self).__init__()
        self.target = target.detach()

    def forward(self, input):
        self.loss = F.mse_loss(input, self.target)
        return input

def gram_matrix(input):
    a, b, c, d = input.size()  
    
    features = input.view(a * b, c * d) 

    G = torch.mm(features, features.t())

    return G.div(a * b * c * d)

class StyleLoss(nn.Module):

    def __init__(self, target_feature):
        super(StyleLoss, self).__init__()
        self.target = gram_matrix(target_feature).detach()

    def forward(self, input):
        G = gram_matrix(input)
        self.loss = F.mse_loss(G, self.target)
        return input

cnn_normalization_mean = torch.tensor([0.485, 0.456, 0.406]).to(device)
cnn_normalization_std = torch.tensor([0.229, 0.224, 0.225]).to(device)

class Normalization(nn.Module):
    def __init__(self, mean, std):
        super(Normalization, self).__init__()
        self.mean = torch.tensor(mean).view(-1, 1, 1)
        self.std = torch.tensor(std).view(-1, 1, 1)

    def forward(self, img):
        return (img - self.mean) / self.std

content_layers_default = ['conv_4']
style_layers_default = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']



def get_style_model_and_losses(cnn, normalization_mean, normalization_std,
                               style_img, content_img,
                               content_layers=content_layers_default,
                               style_layers=style_layers_default):
    cnn = copy.deepcopy(cnn)

    normalization = Normalization(normalization_mean, normalization_std).to(device)

    content_losses = []
    style_losses = []

    model = nn.Sequential(normalization)

    i = 0
    for layer in cnn.children():
        if isinstance(layer, nn.Conv2d):
            i += 1
            name = 'conv_{}'.format(i)
        elif isinstance(layer, nn.ReLU):
            name = 'relu_{}'.format(i)
            layer = nn.ReLU(inplace=False)
        elif isinstance(layer, nn.MaxPool2d):
            name = 'pool_{}'.format(i)
        elif isinstance(layer, nn.BatchNorm2d):
            name = 'bn_{}'.format(i)
        else:
            raise RuntimeError('Unrecognized layer: {}'.format(layer.__class__.__name__))

        model.add_module(name, layer)

        if name in content_layers:
            target = model(content_img).detach()
            content_loss = ContentLoss(target)
            model.add_module("content_loss_{}".format(i), content_loss)
            content_losses.append(content_loss)

        if name in style_layers:
            target_feature = model(style_img).detach()
            style_loss = StyleLoss(target_feature)
            model.add_module("style_loss_{}".format(i), style_loss)
            style_losses.append(style_loss)

    for i in range(len(model) - 1, -1, -1):
        if isinstance(model[i], ContentLoss) or isinstance(model[i], StyleLoss):
            break

    model = model[:(i + 1)]

    return model, style_losses, content_losses

def get_input_optimizer(input_img):
    optimizer = optim.LBFGS([input_img.requires_grad_()])
    return optimizer

def run_style_transfer(cnn, normalization_mean, normalization_std,
                       content_img, style_img, input_img, num_steps=300,
                       style_weight=100000, content_weight=0.3):
    print('Building the style transfer model..')
    model, style_losses, content_losses = get_style_model_and_losses(cnn,
        normalization_mean, normalization_std, style_img, content_img)
    optimizer = get_input_optimizer(input_img)

    print('Optimizing..')
    run = [0]
    while run[0] <= num_steps:

        def closure():
            input_img.data.clamp_(0, 1)
            optimizer.zero_grad()
            model(input_img)
            style_score = 0
            content_score = 0

            for sl in style_losses:
                style_score += sl.loss
            for cl in content_losses:
                content_score += cl.loss

            style_score *= style_weight
            content_score *= content_weight

            loss = style_score + content_score
            loss.backward()

            run[0] += 1
            if run[0] % 50 == 0:
                print("run {}:".format(run))
                print('Style Loss : {:4f} Content Loss: {:4f}'.format(
                    style_score.item(), content_score.item()))
                print()
            return style_score + content_score

        optimizer.step(closure)

    input_img.data.clamp_(0, 1)

    return input_img

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/transfer', methods=['POST', 'GET'])
def transfer():
    if request.method == 'POST':
       content_type = request.form.get('content_type')
       if content_type == 'upload':
            if 'content_image' not in request.files or 'style_image' not in request.files:
                return jsonify({'error': 'Content and style images are required.'}), 400
            content_file = request.files['content_image']
            
            
        # elif content_type == 'text':
        #     text_prompt = request.form.get('text_prompt')
        #     content_img = generate_image(text_prompt, image_gen_model)
        #     content_path = os.path.join(UPLOAD_FOLDER, "content.png")
        #     vutils.save_image(content_img, content_path)
        #     img_byte_array = io.BytesIO()
        #     content_img.save(img_byte_array, format='JPEG')
        #     img_byte_array.seek(0)
        #     return send_file(img_byte_array, mimetype='image/jpeg')
            #return jsonify({'image': content_img}), 200 
        # else:
        #     return jsonify({'error': 'Invalid content type.'}), 400
            content_path = os.path.join(UPLOAD_FOLDER, content_file.filename)
            content_file.save(content_path)
            style_file = request.files['style_image']
            style_path = os.path.join(UPLOAD_FOLDER, style_file.filename)
            style_file.save(style_path)

            content_img = image_loader(content_path)
            style_img = image_loader(style_path)
            style_img = style_img[:, :3, :, :]
            content_img = content_img[:, :3, :, :]
            input_img = content_img.clone()
            output = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std,
                                        content_img, style_img, input_img)
            output_path = os.path.join(OUTPUT_FOLDER, "output.png")
            vutils.save_image(output, output_path)
    return jsonify({'success': 'Image transfer successful.'}), 200

@app.route('/get_output', methods= ['POST'])
def result():
    output_directory="C:/Users/aleen/Desktop/Mainproject/static/output.png"
    return send_file(output_directory, mimetype='image/jpeg/png')      
if __name__ == '__main__':
    app.run(debug=True)
