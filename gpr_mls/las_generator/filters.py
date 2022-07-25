import laspy
import numpy as np
# import open3d as o3d


def rectifier(name, param):
    las = laspy.read(name)

    if param == 'abs':
        las.Amplitude = np.abs(las.Amplitude)
    elif param == 'pos':
        las.points = las.points[las.Amplitude >= 0]
    elif param == 'neg':
        las.points = las.points[las.Amplitude < 0]
    else:
        print('Zły argument filtra rectifier!')

    las.write(name)


def threshold(name, lvl):
    las = laspy.read(name)
    las.points = las.points[np.abs(las.Amplitude) > lvl]
    las.write(name)


def depth_limit(name, limit):
    las = laspy.read(name)
    h_max = max(las.z)
    las.points = las.points[las.z > h_max - limit]
    las.write(name)


# def display_inlier_outlier(cloud, ind):
#     inlier_cloud = cloud.select_down_sample(ind)
#     outlier_cloud = cloud.select_down_sample(ind, invert=True)
#
#     print("Showing outliers (red) and inliers (gray): ")
#     outlier_cloud.paint_uniform_color([1, 0, 0])
#     inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
#     o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])
#
#
# if __name__ == "__main__":
#
#     print("Load a ply point cloud, print it, and render it")
#     pcd = o3d.io.read_point_cloud("../../TestData/ICP/cloud_bin_2.pcd")
#     o3d.visualization.draw_geometries([pcd])
#
#     print("Downsample the point cloud with a voxel of 0.02")
#     voxel_down_pcd = pcd.voxel_down_sample(voxel_size=0.02)
#     o3d.visualization.draw_geometries([voxel_down_pcd])
#
#     print("Every 5th points are selected")
#     uni_down_pcd = pcd.uniform_down_sample(every_k_points=5)
#     o3d.visualization.draw_geometries([uni_down_pcd])
#
#     print("Statistical oulier removal")
#     cl, ind = voxel_down_pcd.remove_statistical_outlier(nb_neighbors=20,
#                                                         std_ratio=2.0)
#     display_inlier_outlier(voxel_down_pcd, ind)
#
#     print("Radius oulier removal")
#     cl, ind = voxel_down_pcd.remove_radius_outlier(nb_points=16, radius=0.05)
#     display_inlier_outlier(voxel_down_pcd, ind)