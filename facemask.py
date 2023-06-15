import os
import numpy as np
import cv2
import datetime
from keras.models import Sequential, load_model
from keras.layers import Conv2D, MaxPooling2D, SpatialDropout2D, Flatten, Dropout, Dense
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
import keras.utils as image


# Check if the model file exists
if os.path.exists('mymodel.h5'):
    # Load the pre-trained model
    mymodel = load_model('mymodel.h5')
else:
    # BUILDING MODEL TO CLASSIFY BETWEEN MASK AND NO MASK
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)))
    model.add(MaxPooling2D())
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D())
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D())
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

    test_datagen = ImageDataGenerator(rescale=1./255)

    training_set = train_datagen.flow_from_directory(
        'train',
        target_size=(150, 150),
        batch_size=16,
        class_mode='binary')

    test_set = test_datagen.flow_from_directory(
        'test',
        target_size=(150, 150),
        batch_size=16,
        class_mode='binary')

    model.fit_generator(
        training_set,
        epochs=10,
        validation_data=test_set,
    )

    model.save('mymodel.h5')
    mymodel = model

# IMPLEMENTING LIVE DETECTION OF FACE MASK

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

while cap.isOpened():
    _, img = cap.read()
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=4)
    
    for (x, y, w, h) in faces:
        face_img = img[y:y+h, x:x+w]
        cv2.imwrite('temp.jpg', face_img)
        test_image = image.load_img('temp.jpg', target_size=(150, 150, 3))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis=0)
        pred = mymodel.predict(test_image)[0][0]
        
        if pred == 1:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
            cv2.putText(img, 'NO MASK', ((x+w)//2, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        else:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(img, 'MASK', ((x+w)//2, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        
        datet = str(datetime.datetime.now())
        cv2.putText(img, datet, (400, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
          
    cv2.imshow('img', img)
    
    if cv2.waitKey(1) == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
