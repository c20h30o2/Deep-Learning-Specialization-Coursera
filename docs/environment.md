# Windows + VS Code + uv

## 首次安装

适用于 Windows 10/11 **x64**，默认使用 CPU。先安装 Git 和 VS Code；Python、uv 和课程依赖由脚本准备。
在 PowerShell 中执行（建议使用 `C:\src` 等短目录）：

```powershell
git clone -c core.longpaths=true https://github.com/c20h30o2/Deep-Learning-Specialization-Coursera.git C:\src\dls
cd C:\src\dls
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
code .
```

脚本会按需使用 [uv 官方安装器](https://docs.astral.sh/uv/getting-started/installation/)，检查 TensorFlow 所需的 Microsoft C++ x64 运行库，执行 `uv sync --locked`，运行环境自检，最后注册 **DLS Labs (uv Python 3.10)** 内核。安装 C++ 运行库时可能出现 Windows 管理员授权窗口。已有 uv 需为 0.12.19 或更新版本。

首次安装需要联网下载 Python 和较大的机器学习包，预留数 GB 空间。TensorFlow 在原生 Windows 上需要 C++ 运行库，详见 [TensorFlow 安装要求](https://www.tensorflow.org/install/pip#windows-native)。无需安装 CUDA 或 Anaconda。

Python 包默认从清华 PyPI 镜像下载，PyTorch CPU 包使用 PyTorch 官方源；版本和校验值记录在锁文件中。网络需能访问这些源及 Python 下载使用的 GitHub。

在 VS Code 中：

1. 打开整个仓库目录，安装推荐的 **Python** 和 **Jupyter** 扩展。
2. 打开 `.ipynb`，点击右上角 **Select Kernel → Select Another Kernel → Jupyter Kernel → DLS Labs (uv Python 3.10)**。
3. 使用此命名内核可确保中文 Windows 上以 UTF-8 读取文本。第一次可能需要重新加载 VS Code 才能看到它。

工作区已配置 `.venv` 解释器，并让 notebook 从自身所在目录运行，以便找到 `utils.py`、`images/`、`datasets/` 等相对路径。不要单独把 notebook 复制到别处执行。

## 后续使用

```powershell
git pull
uv sync --locked
```

打开 notebook，继续选择上述内核即可。不需要激活虚拟环境或逐个安装库。
如果移动了整个仓库目录，重新运行安装脚本以更新内核中的解释器路径。

手动检查环境：

```powershell
uv run --locked python scripts/check_environment.py
uv pip check
```

`pyproject.toml` 声明依赖，`uv.lock` 固定直接及间接依赖和下载校验值，`.python-version` 指定 Python 3.10.21。
不要执行各 lab 遗留的 `pip install -r requirements.txt`，也不要在 notebook 中随意升级 TensorFlow、Keras、NumPy 或 Transformers；修改依赖后应重新生成并提交锁文件。

## 兼容范围

| 内容 | 配置 |
| --- | --- |
| 平台 | Windows x64、Linux x86_64 |
| Python | 3.10.21 |
| 深度学习 | TensorFlow 2.10.1、Keras 2.10.0、PyTorch 2.2.2 CPU |
| 科学计算 | NumPy 1.23.5、SciPy 1.10.1、pandas 1.5.3、scikit-learn 1.2.2 |
| Notebook | ipykernel、IPython、ipywidgets |
| 序列模型 | music21、mido、pydub、Faker、Babel、emoji |
| Transformer bonus | Transformers、datasets、pyarrow、seqeval、accelerate |

版本优先兼容原课程代码：保留 `np.int` / `np.bool`、旧 Keras preprocessing 和 `emoji.emojize(use_aliases=True)` 等接口。课程内部的精确数值、模型结构断言仍可能受原教学环境版本影响。自检涵盖导入、微型模型训练、HDF5 保存/加载、两种 Transformer 后端、数据集读写、MIDI/WAV 和真实 Jupyter 内核启动；不执行所有未完成的作业。

Course 2 目录名中的冒号已替换为 ` -`，避免 Windows 检出失败。克隆命令为本仓库启用 Git 长路径支持；仍建议使用短路径。

另做了三处环境兼容调整：Emoji 测试从当前 Keras 导入 `Functional`；风格迁移工具使用 Pillow 保存图片，替代已移除的 `scipy.misc.imsave`；NER bonus 不再在运行时执行 `pip install seqeval`。练习答案不受影响。

Linux 下安装 uv 后执行 `uv sync --locked` 和上述自检命令即可；可使用 `.venv/bin/python` 作为内核。macOS、Windows ARM64 和 GPU 环境不在此锁文件的验证范围内。

## 数据集与课程文件

**依赖安装不会补齐数据集、预训练模型或作业答案。** 原作者将大文件放在 Google Drive，仓库根目录的 `.gitignore` 还忽略了部分 `.h5`、音频和模型文件；仅 `git pull` 无法获得它们。

开始某个 lab 前，按该目录下 `README.md` 的链接下载并放入指定目录。这包括猫狗/图像数据、YOLO 与 FaceNet 模型、GloVe 词向量、爵士 MIDI、触发词音频，以及 Transformer bonus 的模型、tokenizer 和数据集。下载链接和文件可用性由原作者维护。

仓库中的 `generateTestCases.py` 是课程出题工具，部分依赖未公开的 `solutions`、`grader_support`、`testCase`；这些不是可通过 uv 安装的学生运行依赖。按 notebook 中的公开测试做题即可。

课程使用的 WAV 读写和 MIDI 处理包含在自检中；自行扩展到 MP3 转码或外部乐谱显示时，才需另行安装 FFmpeg 或乐谱软件。

GitHub Actions 的 **Lab environment** 工作流会在 Windows 和 Linux 上重新安装锁定环境并运行自检，可在仓库 Actions 页查看实际结果。
