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
        print(f"Seed point {i}: {point}, closest surface point ID: {point_id}")

    centerline_filter.SeedIds = seed_ids
    
    try:
        print("Starting centerline extraction...")
        centerline_filter.Execute()
        print("Centerline extraction completed.")
    except Exception as e:
        print(f"An error occurred during centerline extraction: {e}")
        return None

    return centerline_filter.Centerlines

# 保存中心线为VTP文件
def save_centerline(centerline, filename):
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(centerline)
    writer.Write()

# 渲染表面和中心线
def render_surface_and_centerline(surface, centerline, seed_points):
    # 创建渲染器和渲染窗口
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    render_window_interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    # 显示表面模型
    surface_mapper = vtk.vtkPolyDataMapper()
    surface_mapper.SetInputData(surface)
    surface_actor = vtk.vtkActor()
    surface_actor.SetMapper(surface_mapper)
    surface_actor.GetProperty().SetOpacity(0.5)  # 设置表面透明度
    renderer.AddActor(surface_actor)

    # 显示中心线
    if centerline is not None:
        centerline_mapper = vtk.vtkPolyDataMapper()
        centerline_mapper.SetInputData(centerline)
        centerline_actor = vtk.vtkActor()
        centerline_actor.SetMapper(centerline_mapper)
        centerline_actor.GetProperty().SetColor(1, 0, 0)  # 红色
        centerline_actor.GetProperty().SetLineWidth(2)  # 设置线宽
        renderer.AddActor(centerline_actor)
    else:
        print("No centerline to display.")

    # 显示种子点
    seed_points_polydata = vtk.vtkPolyData()
    seed_points_polydata.SetPoints(seed_points)

    vertices = vtk.vtkCellArray()
    for i in range(seed_points.GetNumberOfPoints()):
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(i)

    seed_points_polydata.SetVerts(vertices)

    seed_points_mapper = vtk.vtkPolyDataMapper()
    seed_points_mapper.SetInputData(seed_points_polydata)

    seed_points_actor = vtk.vtkActor()
    seed_points_actor.SetMapper(seed_points_mapper)
    seed_points_actor.GetProperty().SetColor(0, 1, 0)  # 绿色
    seed_points_actor.GetProperty().SetPointSize(8)
    renderer.AddActor(seed_points_actor)

    # 设置渲染器背景和窗口大小
    renderer.SetBackground(0.1, 0.2, 0.4)
    render_window.SetSize(800, 600)

    # 开始渲染
    render_window.Render()
    render_window_interactor.Start()

if __name__ == "__main__":
    stl_filename = 'KONG.stl'
    
    # 创建并添加初始种子点
    seed_points = vtk.vtkPoints()
    # 根据经验或先前的观察来添加种子点
    # 这里的点需要根据具体情况进行调整
    seed_points.InsertNextPoint(-3.966476552665317, -43.14313058291623, 118.83881773014947)
    seed_points.InsertNextPoint(-67.39843208006597, -44.04273346171593, -182.42530036307252)
    seed_points.InsertNextPoint(-62.4652955865815, -67.8254269940835, -182.4254933122624)
    seed_points.InsertNextPoint(-18.574133333481782, -16.38647060413977, -39.97389681298807)
    seed_points.InsertNextPoint(48.80668138669203, -18.054499325834456, -48.639337590515204)
    seed_points.InsertNextPoint(74.21835460471749, -70.01416543478689, -182.3997646288004)
    seed_points.InsertNextPoint(91.30590662457553, -55.65445365240457, -182.40147211680664)
    
    # 读取STL文件
    surface = read_stl_file(stl_filename)
    
    # 提取中心线
    centerline = extract_centerline(surface, seed_points)
    
    if centerline is not None:
        # 保存中心线为VTP文件
        save_centerline(centerline, 'centerline_from_initial_seed_points.vtp')
        print("Centerline extraction completed and saved to centerline_from_initial_seed_points.vtp")
    
    # 渲染表面和中心线
    render_surface_and_centerline(surface, centerline, seed_points)
