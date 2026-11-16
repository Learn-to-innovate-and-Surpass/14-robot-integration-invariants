# 机器人集成中的语义与结构布局不变量

错误单位、姿态语义、参考系或结构体打包范围，可能让“数值正常”的集成结果失真。本仓用六分量位姿校验、显式单位转换、独立假反馈和局部 C++ 打包示例，展示如何在边界处拒绝错误。

这是本次整理新写的离线参考实现，不是历史生产原件。不含机器人接口、真实位姿、标定、运动命令、SDK、设备地址或现场数据。

## 运行

Python 3.10+，仅标准库：

```text
python demo.py
python -m unittest discover -s tests -v
```

可选 C++11 示例，使用本地编译器编译**两个**编译单元：

```text
g++ -std=c++11 -Wall -Wextra -pedantic cpp/layout_demo.cpp cpp/layout_peer.cpp -o layout_demo
```

运行生成的 `layout_demo`（Windows 为 `layout_demo.exe`）。MSVC 可使用：

```text
cl /EHsc /W4 cpp/layout_demo.cpp cpp/layout_peer.cpp /Fe:layout_demo.exe
```

编译期断言检查打包记录及普通记录的对齐；运行期检查两个编译单元大小与偏移一致。编译输出属于本地验证产物，不应纳入源码发布。

## 方法与边界

`Pose6` 显式携带长度/角度单位、参考系、工具和姿态约定。标准形式为 mm 与 rad；旋转约定为主动 `Rz(yaw) Ry(pitch) Rx(roll)`。反馈比较使用平移距离和四元数角差，`q` 与 `-q` 等价。假执行器要求显式直线语义、完成回执和独立实际位姿同时成立。

详见 [METHODS.md](METHODS.md)。软件回执和位姿差不能证明插牢、导通、无碰撞、TCP 精度或整机验收。本仓不实施运动，不提供生产容差建议。

MIT 仅覆盖新写的公开代码、说明及合成示例，不包括任何原系统、厂家库或协议。
