import os
import weakref
import numpy as np
import dezero.functions as F
from dezero.core import Parameter

class Layer:
  def __init__(self):
    self._params = set()

  def __setattr__(self, name, value):
    if isinstance(value, (Parameter, Layer)):
      self._params.add(name)
    super().__setattr__(name,value)

  def __call__(self, *inputs):
    outputs = self.forward(*inputs)
    if not isinstance(outputs, tuple):
      outputs = (outputs,)
    self.outputs = [weakref.ref(y) for y in outputs]
    return outputs if len(outputs) > 1 else outputs[0]

  def forward(self, inputs):
    raise NotImplementedError()

  def params(self):
    for name in self._params:
      obj = self.__dict__[name]
      if isinstance(obj, Layer):
        yield from obj.params()
      else:
        yield obj
   
  

  def _flatten_params(self, params_dict, parent_key = ''):
    for name in self._params:
      obj = self.__dict__[name]
      key = parent_key + '/' + name if parent_key else name

      if isinstance(obj, Layer):
        obj._flatten_params(params_dict, key)

      else: 
        params_dict[key] = obj
        

  def cleargrads(self):
    for param in self.params():
      param.cleargrad()


class Linear(Layer):
  def __init__(self, out_size, nobias = False, dtype = np.float32, in_size = None):
    super().__init__()
    self.in_size = in_size
    self.out_size = out_size
    self.dtype = dtype

    self.W = Parameter(None, name='W')
    if self.in_size is not None:
      self._init_w()

    if nobias:
      self.b = None

    else :
      self.b = Parameter(np.zeros(out_size,dtype=dtype),name='b')

  def _init_W(self):
    I, O = self.in_size, self.out_size
    W_data = np.random.randn(I, O).astype(self.dtype) * np.sqrt(1 / I)
    self.W.data = W_data

  def forward(self, x):
    if self.W.data is None:
      self.in_size = x.shape[1]
      self._init_W()

    y = F.linear(x, self.W, self.b)
    return y
    
