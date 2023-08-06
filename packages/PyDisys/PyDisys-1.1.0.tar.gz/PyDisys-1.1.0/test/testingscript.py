import sys
sys.path.insert(1, "C:\\Users\\disys\\Desktop\\REPOS\\DisysLibrary\\src")

import Disys_Calib as dc
import pandas as pd

cam_sn = "40194215"
output_path = "C:\\Users\\disys\\Desktop\\REPOS\\DisysLibrary\\test\\40194215"
df = pd.read_csv("C:\\Users\\disys\\Desktop\\REPOS\\DisysLibrary\\test\\calibration.csv", sep=' ')
width = 1936
height = 1216

testobj = dc.Disys_Calib(df, output_path, cam_sn)
net_mlp, net_prn = testobj.CreateNN(width, height)
net_mlpMI, net_prnMI = testobj.MatriceInversaNN()
testobj.CreateLuts(net_mlp, width, height)
testobj.MoveFilesToFolders()
testobj.PointsWithMaxErr(10)