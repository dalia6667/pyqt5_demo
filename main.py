from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication, QPushButton, QVBoxLayout, QWidget
import sys
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.renderer = vtk.vtkRenderer()
        
        # 创建 vtkRenderWindow
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)

        # 创建 interactor，并设置 render window
        self.interactor = QVTKRenderWindowInteractor(self)
        self.interactor.SetRenderWindow(self.renderWindow)
        
        # 设置主窗口的中心部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        # 创建按钮
        self.open_button = QPushButton("打开 STL 文件", self)
        self.open_button.clicked.connect(self.on_action_open_triggered2)
        self.open_seg_button = QPushButton("seg STL 文件", self)
        self.open_seg_button.clicked.connect(self.on_action_seg_triggered)
        layout.addWidget(self.open_button)
        layout.addWidget(self.open_seg_button)
        layout.addWidget(self.interactor)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('STL Viewer')
        self.interactor.Initialize()
        self.interactor.Start()

    def on_action_seg_triggered(self):
        # 获取场景中的最后一个Actor
        actor = self.renderer.GetActors().GetLastActor()
        if not actor:
            QMessageBox.warning(self, "警告", "没有可用的模型")
            return
        
        # 获取模型数据
        poly_data = vtk.vtkPolyData.SafeDownCast(actor.GetMapper().GetInput())
        if not poly_data:
            QMessageBox.warning(self, "警告", "无法获取模型数据")
            return
        
        # 创建切割平面
        plane = vtk.vtkPlane()
        plane.SetOrigin(0, 0, 0)
        plane.SetNormal(0.0, 0.0, 1.0)
        
        # 创建切割器
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(poly_data)
        cutter.Update()
        
        # 创建Stripper，用于连接切割后的线段
        stripper = vtk.vtkStripper()
        stripper.SetInputData(cutter.GetOutput())
        stripper.Update()
        
        # 获取连接后的线段数据
        stripped_data = stripper.GetOutput()
        
        # 计算每个切片的质心
        points = stripped_data.GetPoints()
        lines = stripped_data.GetLines()
        lines.InitTraversal()
        pt_ids = vtk.vtkIdList()
        
        while lines.GetNextCell(pt_ids):
            npts = pt_ids.GetNumberOfIds()
            centroid = [0.0, 0.0, 0.0]
            for i in range(npts):
                point = points.GetPoint(pt_ids.GetId(i))
                centroid[0] += point[0]
                centroid[1] += point[1]
                centroid[2] += point[2]
            centroid = [c / npts for c in centroid]
            
            print(f"Centroid: ({centroid[0]}, {centroid[1]}, {centroid[2]})")
    def on_action_open_triggered2(self):
        # 打开文件对话框以选择STL文件
        file_name, _ = QFileDialog.getOpenFileName(self, "打开STL文件", "", "STL Files (*.stl)")
        if not file_name:
            return
        
        # 加载STL文件
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_name)
        reader.Update()
        
        # 检查是否成功获取模型数据
        poly_data = reader.GetOutput()
        if not poly_data or poly_data.GetNumberOfPoints() == 0:
            QMessageBox.warning(self, "警告", "无法加载模型")
            return
        else:
            QMessageBox.information(self, "提示", "成功加载模型")
        
        # 创建Mapper和Actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        # 添加Actor到Renderer
        self.renderer.AddActor(actor)
        
        # 计算模型的边界范围
        bounds = poly_data.GetBounds()
        
        # 计算模型中心
        center = [(bounds[0] + bounds[1]) / 2.0, (bounds[2] + bounds[3]) / 2.0, (bounds[4] + bounds[5]) / 2.0]
        
        # 设置相机的位置和焦点，将模型显示在窗口中心
        camera_pos = [center[0], center[1], bounds[5] + 2 * (bounds[5] - bounds[4])]
        focal_point = [center[0], center[1], center[2]]
        
        # 获取当前相机
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(camera_pos)
        camera.SetFocalPoint(focal_point)
        
        # 设置相机的视角
        camera.SetViewAngle(30)
        
        # 渲染
        self.renderWindow.Render()
    def on_action_open_triggered(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开STL文件", "", "STL Files (*.stl)")
        if not file_name:
            return
        
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_name)
        reader.Update()

        poly_data = reader.GetOutput()
        if not poly_data or poly_data.GetNumberOfPoints() == 0:
            QMessageBox.warning(self, "警告", "无法加载模型")
            return
        else:
            QMessageBox.information(self, "提示", "成功加载模型")
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        
        bounds = poly_data.GetBounds()
        center = [(bounds[0] + bounds[1]) / 2.0, (bounds[2] + bounds[3]) / 2.0, (bounds[4] + bounds[5]) / 2.0]
        
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition([center[0], center[1], bounds[5] + 2 * (bounds[5] - bounds[4])])
        camera.SetFocalPoint(center)
        camera.SetViewAngle(30)
        
        self.renderWindow.Render()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
