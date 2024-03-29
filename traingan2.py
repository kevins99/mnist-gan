import keras
from keras.models import Model
from keras import layers as L
import numpy as np
import cv2
from tqdm import tqdm

last_finished_epoch = 85  # models saved every 5 epochs so must be a multiple of 5
epochs = 500
batch_size = 200
dvsgr = 2
steps_per_epoch = 200

(X_train, _), (_, _) = keras.datasets.mnist.load_data()
X_train = np.array(X_train)
X_train = X_train.astype(float)/255.0


def create_gan(discriminator, generator):
    discriminator.trainable = False
    gan_input = L.Input(shape=(100,))
    x = generator(gan_input)
    gan_output = discriminator(x)
    gan = Model(inputs=gan_input, outputs=gan_output)
    gan.compile(loss=keras.losses.binary_crossentropy,
                optimizer=keras.optimizers.adam(0.001))
    return gan


generator = keras.models.load_model(
    'checkpoint_models/mnistgeneratorep'+str(last_finished_epoch)+'.hdf5')
discriminator = keras.models.load_model(
    'checkpoint_models/mnistdiscriminatorep'+str(last_finished_epoch)+'.hdf5')
gan = create_gan(discriminator, generator)
print(gan.summary())

for e in range(last_finished_epoch+1, epochs+1):
    print("Epoch %d" % e)
    for _ in tqdm(range(steps_per_epoch)):
        noise = np.random.normal(0, 1, [batch_size, 100])
        generated_images = generator.predict(noise)
        image_batch = X_train[np.random.randint(
            low=0, high=X_train.shape[0], size=batch_size)]
        image_batch = image_batch.reshape((-1, 28, 28, 1))
        X = np.concatenate([image_batch, generated_images])
        y_dis = np.zeros(2*batch_size)
        y_dis[:batch_size] = 1
        discriminator.trainable = True
        for _ in range(dvsgr):
            discriminator_loss = discriminator.train_on_batch(X, y_dis)
        noise = np.random.normal(0, 1, [batch_size, 100])
        y_gen = np.ones(batch_size)
        discriminator.Trainable = False
        gan_loss = gan.train_on_batch(noise, y_gen)
    pr = generator.predict(np.random.normal(0, 1, [1, 100]))
    pr = pr.reshape(28, 28)
    pr = (pr*255.0).astype(int)
    cv2.imwrite('epoch_gen_imgs/prmnist'+str(e)+'.jpg', pr)
    print("Discriminator loss="+str(discriminator_loss))
    print("GAN loss="+str(gan_loss))
    if e % 5 == 0:
        generator.save('checkpoint_models/mnistgeneratorep'+str(e)+'.hdf5')
        discriminator.save(
            'checkpoint_models/mnistdiscriminatorep'+str(e)+'.hdf5')
generator.save('mnistgenerator.hdf5')
discriminator.save('mnistdiscriminator.hdf5')
pr = generator.predict(np.random.normal(0, 1, [1, 100]), batch_size=1)
pr = pr.reshape(28, 28)
pr = (pr*255.0).astype(int)
cv2.imwrite('mnistpr.jpg', pr)
