import pinn

pinnResizeTolerance = 15
pinnDragTolerance = 15

testDragPos = [250,-30]
testDragDuration = 20

def clickBoard(xPos, yPos):
    hitPinns = []
    for note in pinn.pinnList:
        if abs(xPos - note.xPos) < note.xScale / 2 and abs(yPos - note.yPos) < note.yScale / 2:
            hitPinns.append(note)
    hitPinns.sort(key = lambda hitPinn: hitPinn.layer) # Sorted by layer to prioritize the frontmost Pinns
    if len(hitPinns) > 0:
        selectedPinn = hitPinns[0]
        xOffset = abs(xPos - selectedPinn.xPos) # Storing these offsets and passing them to the drag function ensures that Pinns remain
        yOffset = abs(yPos - selectedPinn.yPos) # in the same position relative to the mouse cursor, even if dragged at high speeds.
        xMaxOffset = (selectedPinn.xScale / 2)
        yMaxOffset = (selectedPinn.yScale / 2)
        if xPos >= selectedPinn.xPos + xMaxOffset - pinnResizeTolerance and yPos >= selectedPinn.yPos + yMaxOffset - pinnResizeTolerance:
            print("Resize attempt detected") # Code for resizing a Pinn will be implemented later
        elif xOffset >= xMaxOffset - pinnDragTolerance or yOffset >= yMaxOffset - pinnDragTolerance:
            dragPinn(selectedPinn,xOffset,yOffset)
        else:
            print("Edit attempt detected") # Code for editing Pinn text will be implemented later
    else:
        print("No pinn found") # Code for clicking the Pinnboard directly will be implemented later

def dragPinn(draggedPinn,xOffset,yOffset):
    draggedPinn.move(testDragPos[0] - xOffset, testDragPos[1] - yOffset)
    # Replace with a loop that repeats until mouse button is released once the backend is connected to the UI

testPinn = pinn.textPinn("Test Pinn", "Test Header", "This is a body text!")

clickBoard(300,0) # Test clicking where there is no Pinn
clickBoard(120,220) # Test clicking the bottom right corner of the Pinn to test resize attempt detection
clickBoard(0,0) # Test clicking the center of the Pinn to test edit attempt detection
clickBoard(120,0) # Test clicking near the edge of the Pinn to initiate a drag using dragPinn()

print(f'Pinn "{testPinn.name}" is now at position ({testPinn.xPos}, {testPinn.yPos})!')
# Should display the Pinn being at the location (130, -30) due to the mock drag position
# and the offset of the mock cursor compared to the Pinn's initial position
