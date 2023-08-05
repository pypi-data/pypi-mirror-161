from measuresNEW import measure_pcc
import torch as tt
import torch.nn.functional as ff
from transforms import generate_kernel
import nibabel as nib
from pathlib import Path
from tools import show_midplanes

path_scan = Path(
    "/run/user/1000/kio-fuse-rWmGuU/sftp/omni/home/stru0039/projects/p13_brain_encoder/phase03/data/scans/aligned_scaled_masked_hemisphere_cropped/gholipour/v3_ras/75x145x130/01-0002_185days_0244.nii.gz"
)
scan = nib.load(path_scan).get_fdata()
scan = tt.from_numpy(scan)[None, None, :].float()
scan = scan.tile([2,1,1,1,1])
kernel_blur = generate_kernel("gaussian", [5, 5, 5], [1, 1, 1])[None, None, :].float()
scan_blur = ff.conv3d(scan, kernel_blur, padding="same")
mask = scan > 0

scan_blur *= mask
y = ff.avg_pool3d(scan, kernel_size=16, stride=16)
z = ff.avg_pool3d(mask.float(), kernel_size=16, stride=16)>0.5
# show_midplanes(scan, "scan", False)
# show_midplanes(scan_blur, "scanblur")
print(y.shape)
show_midplanes(y, "y", False)
show_midplanes(z)
sys.exit()




kernel_pcc = generate_kernel("uniform", [3, 3, 3], [1,1, 1]).float()
show_midplanes(kernel_pcc[None, None, :])
kw_pcc = measure_pcc(
    scan, scan_blur, kernel_pcc, value_smooth=0.0001, reduction_spatial="none"
)

print("kw_pcc", 1-kw_pcc.mean())


X = scan[mask].clone()
print(X.shape)
Y = scan_blur[mask].clone()
mu_x = X.mean()
mu_y = Y.mean()
std_x = X.std()
std_y = Y.std()
cov_xy = ((X - mu_x) * (Y - mu_y)).mean()
old_pcc = 1 - (cov_xy + 0.0001) / (std_x * std_y + 0.0001)
print("old_pcc", old_pcc)


vx = X - tt.mean(X)
vy = Y - tt.mean(Y)
cost = tt.sum(vx * vy) / (tt.sqrt(tt.sum(vx**2)) * tt.sqrt(tt.sum(vy**2)))
print(cost)

vx = tt.sqrt((((X - tt.mean(X)) ** 2).mean()))
vy = tt.sqrt((((Y - tt.mean(Y)) ** 2).mean()))
cost = ((X - tt.mean(X)) * (Y - tt.mean(Y))).mean() / (vx*vy)
print(1- cost)
