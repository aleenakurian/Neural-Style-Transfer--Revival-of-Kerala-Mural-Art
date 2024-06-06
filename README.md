# Neural-Style-Transfer--Revival-of-Kerala-Mural-Art
A technique to revive less popular and renown art styles through neural networks.
The process of artistic style transfer involves addressing the challenge of synthesising images, where the content
of one image is replicated with the stylistic characteristics of another. This innovative art generation application
revolutionises the realm of digital art, seamlessly converting photographs into captivating masterpieces inspired by iconic art
styles like cubism, surrealism etc. Users can also effortlessly apply these styles to their photos, witnessing a remarkable
transformation into digital canvases that echo the distinctive brushstrokes and colour palettes of legendary artists like Vincent
van Gogh, Pablo Picasso, Claude Monet, and Salvador Dalí. The interactive and user-friendly interface ensures accessibility
for both seasoned artists and casual enthusiasts. Prioritising high-resolution and visually stunning results, the system employs
advanced neural network architectures to uphold the authenticity of chosen art styles while preserving the details of the
original image.

The following is an example of how this model performs neural style transfer using a kerala mural painting onto a self portrait of Vincent Van Gogh:

![image](https://github.com/aleenakurian/Neural-Style-Transfer--Revival-of-Kerala-Mural-Art/assets/84180132/6d1d991c-b388-476d-b76c-ab9a54b6f1db)

If we were to utilize an AI generated image of a white rabbit using the well known Stable Diffusion model, using the same mural painting, the result is as follows:

![image](https://github.com/aleenakurian/Neural-Style-Transfer--Revival-of-Kerala-Mural-Art/assets/84180132/e84778cd-6182-430e-9d42-63a10f0a99e7)

The VGG-Network, a Convolutional Neural Network established and fully detailed in, provides the foundation for the
results reported in this paper. Its performance on a standard visual object identification benchmark challenge is
comparable to that of humans. We made use of the feature space that the 19 layer VGG-Network's 16 convolutional and
5 pooling layers provided. The fully connected layers of the VGG19 architecture were discarded for this application,
since classification is not performed in this case.
The VGG19 model was trained on the ImageNet dataset, consisting of over 14 million images belonging to over 21,000
classes. With its extensive ImageNet training, VGG19 functions as a potent feature extractor. ImageNet's millions of
annotated photos have "taught" VGG19 how to identify and distinguish between items in images.
Upon employing the trained VGG19 model, its performance revealed a deficiency in handling style transfer tasks for
paintings boasting a plethora of vibrant hues and intricate patterns, notably exemplified in mural art. To rectify this
shortfall, a decision was made to refine the model's capabilities. Through a process of fine-tuning, the model underwent
training on an eclectic array of artistic genres, ranging from various paintings and sculptures to engravings,
iconography, and, notably, mural art. Impressively, this refined model achieved an outstanding accuracy rate of 97.46%
in the classification of these diverse art forms. This enhanced model demonstrated a remarkable ability to discern
intricate details such as multiple colours, rich patterns, and brushstrokes within the style images, leading to significantly
improved accuracy in style transfer tasks. The model's performance exemplifies the intricate dance between art and
technology, where computational methods enhance our understanding and appreciation of artistic expression in all its
diverse forms.
