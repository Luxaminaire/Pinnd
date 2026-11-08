import unittest
import pinn

def prep(imagePinn,xScale,yScale,imageSizeX,imageSizeY):
    imagePinn.xScale = xScale
    imagePinn.yScale = yScale
    imagePinn.imageSizeX = imageSizeX
    imagePinn.imageSizeY = imageSizeY

def test_image_size_equal():
    imagePinn = pinn.imagePinn("Equal Pinn","Test","")
    prep(imagePinn,100,50,100,50)
    assert imagePinn.readjustSize() == False # Pinn should not resize if it is the same size as the image

def test_image_size_smaller():
    imagePinn = pinn.imagePinn("Smaller Pinn", "Test", "")
    prep(imagePinn,100,50,101,51)
    assert imagePinn.readjustSize() == True # Pinn should resize if it is smaller than the image

def test_image_size_larger():
    imagePinn = pinn.imagePinn("Larger Pinn", "Test", "")
    prep(imagePinn, 100, 50, 10, 5)
    assert imagePinn.readjustSize() == False  # Pinn should not resize if it is larger than the image

def test_image_size_invalid():
    imagePinn = pinn.imagePinn("Invalid Pinn", "Test", "")
    prep(imagePinn,100,100,100,-100)
    assert imagePinn.readjustSize() == -1 # Invalid image sizes should return a special value alerting the
                                          # program that something went wrong when importing the image.
                                          # Does not necessarily need to throw an error, as the program can
                                          # simply retry the import and/or present the user with a warning.

# Tests
test_image_size_equal()
test_image_size_smaller()
test_image_size_larger()
test_image_size_invalid()
