from __future__ import division
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import numpy as np 
import random 
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog
from PyQt5.uic import loadUi




PI = math.pi

class Grassfire: 
	'''Used as a container for important constants and functions'''


	# Values to represent all the nodes i.e., the start node, goal node, unvisited nodes, etc.  
	START = 0 
	DEST = -1 
	UNVIS = -2 
	OBST = -3 
	PATH = -4 

	# Colors of all the different nodes/cells 
	COLOR_START = np.array([0, 0.75, 0])
	COLOR_DEST = np.array([0.75, 0, 0])
	COLOR_UNVIS = np.array([1, 1, 1])
	COLOR_VIS = np.array([0, 0.5, 1])
	COLOR_OBST = np.array([0, 0, 0])
	COLOR_PATH = np.array([1, 1, 0])


	def create_grid(self, destRow, destCol, row, col, obstaclePercentage, startingCellCol):
		'''This function returns a matrix that represents the grid and alongwith it, sets the obstacles and the unvisited nodes'''

		numberOfNodes = row * col
		numberOfObstacles = round(numberOfNodes*obstaclePercentage/100)
		
		grid = self.UNVIS * np.ones((row, col), dtype = int) # Create a grid of given rows and columns and set them all as unvisited nodes
		grid[0, startingCellCol-1] = self.START
		grid[destRow-1, destCol-1] = self.DEST
		count = 0 
		
		# Loop to place obstacles by randomly setting nodes as obstacles (Change values from -2 to -3)
		while (count < numberOfObstacles):
			
			obstacle_row = random.randint(0,row-1)
			obstacle_col = random.randint(0,col-1)

			if(grid[obstacle_row, obstacle_col] == self.OBST or grid[obstacle_row, obstacle_col] == self.START or grid[obstacle_row, obstacle_col] == self.DEST):
				continue 
			else: 
				grid[obstacle_row, obstacle_col] = self.OBST
				count += 1    			


		return grid


	def reset_grid(self,grid):
		'''Reset all the cells/nodes that are not obstacles, start, destination or univisited nodes/cells'''

		cellsToReset = ~((grid == self.OBST) + (grid == self.START) + (grid == self.DEST))
		grid[cellsToReset] = self.UNVIS
		
		

	def color_grid(self,grid):
		'''Return a 3-D array that represents the grid visually'''

		(rows, cols) = grid.shape

		colorGrid = np.zeros((rows, cols, 3), dtype = float)

		colorGrid[grid == self.OBST, :] = self.COLOR_OBST
		colorGrid[grid == self.UNVIS, :] = self.COLOR_UNVIS
		colorGrid[grid == self.START, :] = self.COLOR_START
		colorGrid[grid == self.DEST, :] = self.COLOR_DEST
		colorGrid[grid > self.START, :] = self.COLOR_VIS
		colorGrid[grid == self.PATH, :] = self.COLOR_PATH

		return colorGrid


	def check_adjacent(self, grid, cell, currentDepth):
		'''Check the cells that are neighbours of the current cell. If the depth of the neighbours is more than the current depth, 
		then we update those depths with the currents depths. Also check for the destination node. If it is found, we return the DEST constant or
		we return the number of neighbour cells that were updated. '''


		(rows, cols) = grid.shape


		numCellsUpdated = 0


		for i in range(4):
			rowToCheck = cell[0] + int(math.sin((PI/2)*i))
			colToCheck = cell[1] + int(math.cos((PI/2)*i))

			if not(0 <= rowToCheck < rows and 0 <= colToCheck < cols):
				#Check to see if the cells are within bounds
				continue 
			elif grid[rowToCheck, colToCheck] == self.DEST:
				return self.DEST
			# If nieghbouring cells are unvisited or the depth > currentDepth + 1 then 
			# update the depth value of the neighbour cells/nodes
			elif(grid[rowToCheck, colToCheck] == self.UNVIS or grid[rowToCheck, colToCheck] > currentDepth + 1):
				grid[rowToCheck, colToCheck] = currentDepth + 1
				numCellsUpdated += 1 

		return numCellsUpdated


	def backtrack(self, grid, cell, currentDepth):
		'''Function used in case the destination is found. It returns the co-ordinates of the first cell that has a depth that matches the "currentDepth"
		which indirectly means the next cell that is on the path from the destination to the start''' 

		(rows, cols) = grid.shape

		for i in range(4):
			rowToCheck = cell[0] + int(math.sin((PI/2)*i))
			colToCheck = cell[1] + int(math.cos((PI/2)*i))


			if not (0 <= rowToCheck < rows and 0 <= colToCheck < cols):
				continue
			elif grid[rowToCheck, colToCheck] == currentDepth:
				nextCell = (rowToCheck, colToCheck)
				grid[nextCell] = Grassfire.PATH
				return nextCell


	def pathfinder(self, grid):
		''' Executes the grassfire algorithm by first spreading outwards from the starting cell. 
		If the destination is found then the algorithm backtracks from the destination to the start 
		This function returns a generator function so that the program can step through and animate the algorithm'''

		nonlocalDict = {'grid': grid}

		def pathfinder_generator():
			grid = nonlocalDict['grid']
			depth = 0 
			destFound = False 
			cellsExhausted = False 

			while(not destFound) and (not cellsExhausted):
				numCellsModified = 0
				depthIndices = np.where(grid == depth)
				matchingCells = list(zip(depthIndices[0], depthIndices[1]))

				for cell in matchingCells:
					adjacentVal = self.check_adjacent(grid, cell, depth)

					if adjacentVal == self.DEST:
						destFound = True 
						break
					else: 
						numCellsModified += adjacentVal


				if numCellsModified == 0:
					cellsExhausted = True 

				elif not destFound:
					depth += 1 
				yield 


			if destFound: 
				destCell = np.where(grid == self.DEST)
				backtrackCell = (destCell[0].item(), destCell[1].item())
				while depth > 0: 
					nextCell = self.backtrack(grid, backtrackCell, depth)
					backtrackCell = nextCell
					depth -= 1
					yield
		

		return pathfinder_generator	


class MainWindow(QMainWindow):

	
	def __init__(self, *args, **kwargs):
		'''Constructor'''

		super(MainWindow, self).__init__(*args, **kwargs)

		loadUi("GrassfireUI.ui", self)
		ani = None
		grid = None
		

	def run(self):
		''' Function to handle the click of the Run button'''

		try:

			a = self.GridRowsLineEdit.text()
			b = self.GridColumnsLineEdit.text()
			c = self.ObstaclePercentageLineEdit.text()
			d = self.StartingCellLineEdit.text()
			e = self.DestinationRowLineEdit.text()
			f = self.DestinationColumnLineEdit.text()

			if (a == '' or b == '' or c == '' or d == '' or e == '' or f ==''):
				self.statusbar.showMessage("Please fill all the fields", 3000)
				return

			gridRows = int(a)
			gridCol = int(b) 
			obstaclePercentage = int(float(c))
			startingCellCol = int(d)
			destRow = int(e)
			destCol = int(f)

			if(gridRows < 0 or gridCol < 0 or obstaclePercentage < 0 or startingCellCol < 0 or destCol < 0 or destRow < 0):
				self.statusbar.showMessage("Values should be non-negative", 3000)
				return
			
			if(gridRows < 8 or gridCol < 8):
				self.statusbar.showMessage("The Grid should be atleast 8x8", 4000)
				return

			if(obstaclePercentage>20 or obstaclePercentage<10):
				self.statusbar.showMessage("Obstacle Percentage should be in between 10 and 20", 3000)
				return 

			if(startingCellCol>gridCol):
				self.statusbar.showMessage("Column Position of Starting Cell should be less than or equal to the no. of columns in the Grid", 3000)
				return

			if(destRow <= (gridRows/2)):
				self.statusbar.showMessage("Destination Row should be greater than half of the no. of rows in Grid", 3000)
				return

			if(destCol <= math.ceil(gridCol*2/3)):
				self.statusbar.showMessage("Destination Column should be greater than 2/3 of no. of columns in Grid", 3000)
				return

			if(destCol > gridCol or destRow > gridRows):
				self.statusbar.showMessage("Destination column or row cannot be greater than the grid's",3000)
				return


			GrassfireObj = Grassfire()
			grid = GrassfireObj.create_grid(destRow = destRow, destCol = destCol, row = gridRows, col = gridCol, obstaclePercentage = obstaclePercentage, startingCellCol = startingCellCol)
			#print(grid)
			colorGrid = GrassfireObj.color_grid(grid)

			# Initialize the figure, imshow object, etc 
			fig = plt.figure()
			gridPlot = plt.imshow(colorGrid, interpolation = 'nearest')
			ax = gridPlot._axes
			ax.grid(visible = True, ls = 'solid', color = 'k', lw = 1.5)
			ax.set_xticklabels([])
			ax.set_yticklabels([])

			def init_anim():
				'''Plot grid in its initial state by resetting "grid".'''
				GrassfireObj.reset_grid(grid)
				colorGrid = GrassfireObj.color_grid(grid)
				gridPlot.set_data(colorGrid)

			def update_anim(dummyFrameArgument):
				'''Update plot based on values in "grid" ("grid" is updated
				by the generator--this function simply passes "grid" to
				the color_grid() function to get an image array).
				'''
				colorGrid = GrassfireObj.color_grid(grid)
				gridPlot.set_data(colorGrid)		

			obstText = ax.annotate('Obstacle Precentage ='+str(obstaclePercentage), (0.15, 0.01), xycoords='figure fraction')
			colText = ax.annotate('Columns='+str(gridCol), (0.15, 0.04), xycoords='figure fraction')
			rowText = ax.annotate('Rows='+str(gridRows), (0.15, 0.07), xycoords='figure fraction')

			
			ax.set_xlim((0, gridCol))
			ax.set_ylim((gridRows, 0))
			ax.set_xticks(np.arange(0, gridCol+1, 1))
			ax.set_yticks(np.arange(0, gridRows+1, 1))
			gridPlot.set_extent([0, gridCol, 0, gridRows])

			

			# Create an animation object 
			self.ani = animation.FuncAnimation(fig, update_anim, init_func=init_anim, frames = GrassfireObj.pathfinder(grid), repeat = True, interval = 150)

			# Turn on interactive plotting and show the figure 
			plt.ion()
			plt.show(block=True)

				
		except:
			self.statusbar.showMessage("Please input appropriate data", 3000)
			

	def reset_fields(self):
		a = self.GridRowsLineEdit.clear()
		b = self.GridColumnsLineEdit.clear()
		c = self.ObstaclePercentageLineEdit.clear()
		d = self.StartingCellLineEdit.clear()
		e = self.DestinationRowLineEdit.clear()
		f =self.DestinationColumnLineEdit.clear()

	
		
app = QApplication([])
app.setStyle("Fusion")
app.setApplicationName("Grassfire Algorithm")
main_window = MainWindow()
main_window.show()

main_window.RunButton.clicked.connect(main_window.run)
main_window.ResetButton.clicked.connect(main_window.reset_fields)
app.exec_()





























