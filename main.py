import pinn

pinnResizeTolerance = 15
pinnDragTolerance = 15

testDragPos = [250,-30]
testDragDuration = 20

def clickBoard(xPos, yPos):
    selectedPinns = []
    for note in pinn.pinnList:
        if abs(xPos - note.xPos) < note.xScale / 2 and abs(yPos - note.yPos) < note.yScale / 2:
            selectedPinns.append(note)
    selectedPinns.sort(key = lambda note: note.layer)
    if len(selectedPinns) > 0:
        note = selectedPinns[0]
        xOffset = abs(xPos - note.xPos)
        yOffset = abs(yPos - note.yPos)
        xMaxOffset = (note.xScale / 2)
        yMaxOffset = (note.yScale / 2)
        if xPos >= note.xPos + xMaxOffset - pinnResizeTolerance and yPos >= note.yPos + yMaxOffset - pinnResizeTolerance:
            print("Resize attempt detected") # Code for resizing a Pinn will be implemented later
        elif xOffset >= xMaxOffset - pinnDragTolerance or yOffset >= yMaxOffset - pinnDragTolerance:
            dragPinn(note,xOffset,yOffset)
        else:
            print("Edit attempt detected") # Code for editing Pinn text will be implemented later
    else:
        print("No pinn found") # Code for clicking the Pinnboard directly will be implemented later

def dragPinn(note,xOffset,yOffset):
    test = 0
    while test < testDragDuration: # Replace with a loop that repeats until mouse button is released
        note.move(testDragPos[0]-xOffset,testDragPos[1]-yOffset)
        test += 1

testPinn = pinn.textPinn("Test Pinn", "Test Header", "This is a body text!")

clickBoard(300,0) # Test clicking where there is no Pinn
clickBoard(120,220) # Test clicking the bottom right corner of the test Pinn
clickBoard(0,0) # Test clicking the center of the test Pinn where text will be displayed
clickBoard(120,0) # Test clicking near the edge of the test Pinn to initiate a drag

print(f'Pinn "{testPinn.name}" is now at position ({testPinn.xPos}, {testPinn.yPos})!')
# Should display the Pinn being at the location (130, -30) due to the test drag position
# and the offset of the test cursor compared to the test Pinn's initial position
