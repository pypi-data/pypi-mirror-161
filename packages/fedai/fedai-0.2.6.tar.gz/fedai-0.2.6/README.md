fedai
----------

fedai是terracuda.ai联邦学习平台的客户端实现，提供了一套编程操作规范实现了联邦学习服务端和客户端的对接，用户在编写新模型代码或修改已有模型代码时，通过“埋点”方式执行Client相关方法，便可以实现联邦学习服务端与客户端的交互：将客户端模型、参数等传给客户端训练模型，或者将客户端训练的模型、metrics、参数等回传给客户端。

## 安装
1. 使用terracudaai-python/fedai安装(需要git仓库访问权限)
   ```shell
    git clone git@github.com:xeniroio/terracudaai-python.git && \
    cd terracudaai-python/fedai && \
    pip install .
   ```

2. 通过pip直接安装
    ```shell
    pip install fedai
    ```

## Client类method设计
用户在使用fedai时，主要通过Client类实现联邦学习的相关功能，Client类的method有两种设计：
* add方法  
用来记录参数、指标等基本类型（str, float, int）数据，包括添加单一变量方法和批量添加方法（名称后面带s）。
    ```python
    def add_xxx(self, key: str, value: Union[str, float, int]) -> None:
        # 添加单独一个变量
        ...
        
        
    def add_xxxs(self, values: Dict[str, Union[str, float, int]]) -> None:
        # 同时添加多个变量
        ...
    ```

* handle方法  
handle方法主要目的是可以对训练过程施加影响，对handle的对象进行调整甚至替换并返回这个新的对象，从而实现对训练过程的控制。比如，通过handle优化器对象，调整优化器中的学习率，实现自动调参功能，或者替换并返回聚合算法所需的联邦版本优化器。  
如果handle如果需要传入多个参数，则第一个参数必须是需要handle的对象（比如优化器等），以保证validate装饰器的正常使用。
    ```python
    def handle_xxx(self, obj, args) -> ClassOfObj:
        # 从obj中提取需要记录的信息
        ...
    ```

## 使用方法
1. import fedai的Client  
根据所采用的AI框架选择不同的Client类，包括基于Pytorch的TorchClient，基于TensorFlow的TFClient，基于sklearn的SKClient等等，当前已实现了基于Pytorch的TorchClient，导入方法如下：
    ```python
    from fedai.client import TorchClient as Client
    ```
   
2. Client的三种实例化方式  
   * Client默认从环境变量中读取CLIENT_DIR，隐式创建Client实例  --- 减少对用户的代码侵入  
     这种情况下不需要显式执行实例化操作，后面便可以直接使用Client类调用各种add或handle方法，联邦所需数据都会保存在CLIENT_DIR中。

   * 显式传入client_dir参数创建Client实例 --- 调试场景使用  
     这种情况下会优先使用传入的client_dir，联邦数据会保存到指定的client_dir中。

   * 不显式执行Client的实例化，同时环境变量中也不存在CLIENT_DIR --- 禁用Client  
     这种情况下Client的任何作用都会不起作用，通过这种方式可以实现联邦学习代码与集中式机器学习代码的转换---集中式机器学习代码"埋点"插入Client操作就可以当做联邦学习代码使用，禁用Client后便又成为了集中式机器学习。

3. Client.handle_args()  
   通过handle args变量，可以实现两个目的：
   * 记录训练模型的参数；
   * 根据Server端传来的讯息对args中的参数进行修改，起到自动调参的目的。
   ```python
    args = parser.parse_args()
    args = Client.handle_args(args)
   ```
   
4. Client.handle_dataloader()   
   handle_dataloader 的主要目的是记录数据集的数量，作为Server端聚合的权重依据，另一个目的是根据自动调参或聚合算法的需要，对data_loader中的参数进行调整。
    ```python
    train_loader = torch.utils.data.DataLoader(train_dataset,
                                               batch_size=args.train_batch_size,
                                               num_workers=args.num_workers,
                                               shuffle=True)
    train_loader = Client.handle_dataloader(train_loader)
    ```

5. Client.handle_optimizer()  
   根据Server的信息对优化器进行调整，修改优化器中的学习率等参数，实现自动调参，或者替换成与聚合算法相匹配的联邦学习版优化器。
    ```python
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    optimizer = Client.handle_optimizer(optimizer)
    ```

6. Client.handle_criterion()  
   根据Server端讯息对criterion施加控制。
    ```python
    criterion = nn.CrossEntropyLoss()
    criterion = Client.handle_criterion(creterion)
    ```

7. Client.handle_model()   
    主要目的是记录模型权重，在完成训练后将模型权重保存下来供回传给Server端聚合使用。
    ```python
    model = build_model(
        pretrained=args.pretrained_path,
        fine_tune=True,
        num_classes=len(dataset_classes),
        resumed=args.fed_resume_weights
    ).to(device)
    model = Client.handle_model(model)
    ```

8. Client.add_metircs()  
    记录metrics信息，完成训练后回传给Server端用来分析模型的训练状况。
    ```python
      Client.add_scalar(metric_name="loss", value=train_epoch_loss, epoch=epoch, status="training")
      Client.add_scalar(metric_name="loss", value=valid_epoch_loss, epoch=epoch, status="validation")
      Client.add_scalar(metric_name="acc", value=train_epoch_acc, epoch=epoch, status="training")
      Client.add_scalar(metric_name="acc", value=valid_epoch_acc, epoch=epoch, status="validation")
    ```
