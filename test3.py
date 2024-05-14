import vtk
import vmtk.vmtkscripts as vmtkscripts

# 读取STL文件


def read_stl_file(filename):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

# 提取中心线


def extract_centerline(surface, seed_points):
    centerline_filter = vmtkscripts.vmtkCenterlines()
    centerline_filter.Surface = surface

    seed_ids = vtk.vtkIdList()
    point_locator = vtk.vtkPointLocator()
    point_locator.SetDataSet(surface)
    point_locator.BuildLocator()

    for i in range(seed_points.GetNumberOfPoints()):
        point = seed_points.GetPoint(i)
        point_id = point_locator.FindClosestPoint(point)
        seed_ids.InsertNextId(point_id)

    centerline_filter.SeedIds = seed_ids
    centerline_filter.Execute()

    return centerline_filter.Centerlines

# 保存中心线为VTP文件


def save_centerline(centerline, filename):
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(centerline)
    writer.Write()

# 定义一个交互类来获取种子点


class SeedPointInteractor(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, surface, seed_points, callback, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.AddObserver("KeyPressEvent", self.key_press_event)
        self.surface = surface
        self.seed_points = seed_points
        self.callback = callback
        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window_interactor.SetInteractorStyle(self)
        self.render_window_interactor.SetRenderWindow(self.render_window)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(surface)
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.render_window.Render()

    def start(self):
        self.render_window_interactor.Start()

    def left_button_press_event(self, obj, event):
        click_pos = self.render_window_interactor.GetEventPosition()
        picker = vtk.vtkWorldPointPicker()
        picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        world_position = picker.GetPickPosition()
        self.seed_points.InsertNextPoint(world_position)
        print(f"Seed point added at: {world_position}")

    def key_press_event(self, obj, event):
        key = self.render_window_interactor.GetKeySym()
        if key == "g":  # 按下 "g" 键生成中心线
            print("Generating centerline...")
            self.callback(self.surface, self.seed_points)

# 回调函数，在添加种子点后调用提取中心线函数


def update_centerline(surface, seed_points):
    centerline = extract_centerline(surface, seed_points)
    save_centerline(centerline, 'interactive_centerline.vtp')
    print("Centerline updated and saved to interactive_centerline.vtp")


if __name__ == "__main__":
    stl_filename = 'your_vessel_model.stl'
    seed_points = vtk.vtkPoints()

    # 读取STL文件
    surface = read_stl_file(stl_filename)

    # 创建交互器
    interactor = SeedPointInteractor(surface, seed_points, update_centerline)
    interactor.start()
