import os
import sys
script_dir = os.path.dirname(os.path.realpath(__file__))
global_dir = os.path.join(script_dir, "..")
sys.path.append(global_dir)

import tensorflow as tf
from matplotlib import pyplot as plt

#[use]
state = "road"

state_dir = os.path.join(script_dir, "..", "states", state)
sys.path.append(state_dir)

#[gen]
import state_road as st

params = st.params

nnsize = params.get('nnsize', 256)
nn_outputs = 0
posx = params.get('posx', 0)
posy = params.get('posy', 0)
grabsize = params.get('grabsize', 0)

dataset_dir = ""

def set_nn_params():
    global dataset_dir, nn_outputs
    
    for folder_name in os.listdir(state_dir):

        folder_path = os.path.join(state_dir, folder_name)

        # Check if the folder is actually a directory and contains the state value
        if os.path.isdir(folder_path) and "dataset" in folder_name:                                           
            dataset_dir = folder_path

            # List all items in the specified folder
            items = os.listdir(folder_path)

            # Count subfolders
            nn_outputs = sum(1 for item in items if os.path.isdir(os.path.join(folder_path, item)))

            return                
                        
#main flow                        
set_nn_params()

data = tf.keras.utils.image_dataset_from_directory(
    dataset_dir,
    image_size=(nnsize, nnsize)
)

data_iterator = data.as_numpy_iterator()
batch = data_iterator.next()

fig, ax = plt.subplots(ncols=5, figsize=(20,20))
for idx, img in enumerate(batch[0][:5]):
    ax[idx].imshow(img.astype(int))
    ax[idx].title.set_text(batch[1][idx])
plt.show()

data = data.map(lambda x, y: (x/255.0, y))
scaled_iterator = data.as_numpy_iterator()
batch = scaled_iterator.next()

train_size = int(len(data)*.8)
val_size = int(len(data)*.2)+1

train = data.take(train_size)
val = data.skip(train_size).take(val_size)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout

model = Sequential()
model.add(Conv2D(16, (3,3), 1, activation='relu', input_shape=(nnsize,nnsize,3)))
model.add(MaxPooling2D())

model.add(Conv2D(32, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())

model.add(Conv2D(16, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())

model.add(Flatten())

model.add(Dense(nnsize,activation='relu'))
model.add(Dense(nn_outputs, activation='softmax'))

model.compile('adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False), metrics=['accuracy'])
print(model.summary() )

logdir=os.path.join(script_dir,'logs')
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)

hist = model.fit(train, epochs=30, validation_data=val, callbacks=[tensorboard_callback])

fig = plt.figure()
plt.plot(hist.history['loss'], color='teal', label='loss')
plt.plot(hist.history['val_loss'], color='orange', label='val_loss')
fig.suptitle('Loss', fontsize=20)
plt.show()

fig = plt.figure()
plt.plot(hist.history['accuracy'], color='teal', label='accuracy')
plt.plot(hist.history['val_accuracy'], color='orange', label='val_accuracy')
fig.suptitle('Accuracy', fontsize=20)
plt.legend(loc="upper left")
plt.show()

from tensorflow.keras.models import load_model
model_name = state + ".h5"
model.save(os.path.join(state_dir, model_name))
