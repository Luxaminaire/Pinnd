import unittest
from pathlib import Path
import pinn

def test_image_size():
    path = Path(__file__).parent / "TestDim.png"
    imagePinn = pinn.imagePinn("Image Pinn","Test",path)
    assert imagePinn.xScale == 100 and imagePinn.yScale == 250

def test_audio_duration():
    path = Path(__file__).parent / "TestDur.mp3"
    audioPinn = pinn.audioPinn("Audio Pinn", "Test", path)
    assert audioPinn.audioLength == 14.863673469387756

def test_text_parameters():
    textPinn = pinn.textPinn("Parameter Pinn","Test Header","Test Body")
    textPinn.updateBody(color = '#005533')
    assert textPinn.name == "Parameter Pinn"
    assert textPinn.headerText == "Test Header"
    assert textPinn.bodyText == "Test Body"
    assert textPinn.bodyTextColor == "#005533"

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
