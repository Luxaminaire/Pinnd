import unittest
import pinn

def test_image_size():
    imagePinn = pinn.imagePinn("Image Pinn","Test",r"C:\Users\Mary\Desktop\TestDim.png")
    assert imagePinn.xScale == 100 and imagePinn.yScale == 250

def test_text_parameters():
    textPinn = pinn.textPinn("Parameter Pinn","Test Header","Test Body")
    assert textPinn.name == "Parameter Pinn"
    assert textPinn.headerText == "Test Header"
    assert textPinn.bodyText == "Test Body"

def test_pinn_movement():
    textPinn = pinn.textPinn("Movement Pinn", "Test", "Test")
    textPinn.move(100,-100) # Any position except (0,0) would function equally well for this test
    assert textPinn.xPos == 100
    assert textPinn.yPos == -100

def test_pinn_deletion():
    deleteList = []
    for note in pinn.pinnList:
        deleteList.append(note)
    for note in deleteList:
        note.delete()
    assert len(pinn.pinnList) == 0

test_image_size()
test_text_parameters()
test_pinn_movement()
test_pinn_deletion()
