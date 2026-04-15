# from ultralytics import YOLO
# model = YOLO("yolo26n.pt")
# print(type(model.model))
from ultralytics import YOLO
model = YOLO("yolo26n.pt")
print(model.model.yaml)