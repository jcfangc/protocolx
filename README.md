# ProtocolX

**ProtocolX** 是一个先进的 Python Protocol 组合与动态生成工具，支持类型安全的协议合成与运行时检查，适用于构建插件化、解耦、自动化协议体系的现代 Python 工程。

---

## 特性

-   **类型安全**：仅允许 Protocol 子类组成集合。
-   **组合协议唯一性**：任意协议组合，无论顺序如何，生成的匿名 Protocol 类全局唯一且可缓存。
-   **支持 runtime_checkable**：可选开启运行时 `isinstance`/`issubclass` 检查。
-   **pickle/import 兼容**：所有匿名协议类均可序列化，跨进程、分布式环境直接复用。
-   **高性能惰性实现**：协议集合属性延迟计算，内存与性能开销极低。
-   **丰富的单元测试和类型注释**：开发、维护、迁移无压力。

---

## 快速开始

### 安装

```bash
pip install protocolx
# 或者，若本地开发：
pip install -e .
```

### 导入

```python
from protocolx import ProtocolSequence, compose_protocol
from typing import Protocol
```

### 最小用法示例

```python
class Foo(Protocol):
    def foo(self) -> int: ...

class Bar(Protocol):
    def bar(self) -> str: ...

seq = ProtocolSequence([Foo, Bar])
Composed = compose_protocol(seq, runtime=True)

class MyImpl:
    def foo(self) -> int:
        return 42
    def bar(self) -> str:
        return "hello"

assert isinstance(MyImpl(), Composed)  # True
```

## 作为 TypeVar Bound

你可以用组合后的协议类作为泛型类型参数的 bound：

```python
from typing import TypeVar

seq = ProtocolSequence([Foo, Bar])
Composed = compose_protocol(seq)

T = TypeVar("T", bound=Composed)

def process_plugin(plugin: T):
    plugin.foo()
    plugin.bar()
```

---

## 典型应用场景

-   设计可扩展/解耦插件框架的协议约束
-   自动化类型安全的多协议混合
-   在 runtime 环境下动态生成可检测协议组合
-   支持跨进程、分布式环境 protocol 类型统一

---

## API 文档

### ProtocolSequence

```python
ProtocolSequence(protocols: Sequence[type])
```

-   **功能**：构造有序、唯一、类型安全的 Protocol 集合。
-   **常用属性**：

    -   `.names` —— 返回有序协议名元组
    -   `.items`（可迭代）—— 协议类型组成

### compose_protocol

```python
compose_protocol(bases: ProtocolSequence, *, runtime: bool = False) -> type
```

-   **参数**

    -   `bases`：ProtocolSequence，协议组合（顺序无关）
    -   `runtime`：是否支持 `isinstance`/`issubclass` 检查（默认为 `False`）

-   **返回**

    -   匿名协议类（全局唯一、可 pickle/import）

---

## 高级说明

-   支持 Python 3.8+。
-   `ProtocolSequence` 只接受 Protocol 子类，自动去重并按类名排序。
-   `compose_protocol` 所有返回类均自动挂载至虚拟模块 `__anon_protocol__`，确保序列化与反序列化一致。
-   强类型注释，支持 IDE 与 mypy 静态类型检查。

---

## 许可证

本项目采用 MIT License 开源。

---

## 贡献与支持

欢迎 Issue、PR、建议和改进！
