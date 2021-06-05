

from flask import Flask
import os
from datetime import datetime
from datetime import date
from flask import jsonify,request,flash
from flask import send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

#Проверка на БП
def isBP(path):
    if  os.path.isfile(path):
        return False

    listDir = os.listdir(path)
    for item in listDir:
        try:
            datetime.strptime(item,'%d.%m.%Y')
            return True;
        except:
            pass;

    return False;

#Получение описания (любой папки)
def getDescription(path):
    descrition = "";
    try:
        with open(path+"/descrition.txt") as f:
            for line in f:
                descrition+=line;
    except:
        pass;
    return descrition;
        
#Получение списка всех фото в папке
def getAllPhoto(path):
    result = [];
    listDir = os.listdir(path);
    for photoName in listDir:
        if(".jpg" in photoName) or (".png" in photoName):
            result.append(path+"/"+photoName);
    return result;

#обход на папок с фото у БП
def getListpath(path):
    result = [];
    listDir = os.listdir(path);
    for date in listDir:
        try:
            datetime.strptime(date,'%d.%m.%Y')
            listPhoto = getAllPhoto(path+"/"+date);
            item = {
                "listPhoto": listPhoto,
                "descritpion": getDescription(path+"/"+date),
                "date" : date
                }
            result.append(item);
        except:
            pass;
    return result;

#Генерация БП
def genBP(name,path):
    Listpath = getListpath(path+"/"+name);
    item = {
        "name": name,
        "description": getDescription(path+"/"+name),
        "urlImage": findImage(name,path),
        "Listpath": Listpath
        }
    return item;


#Генерация списка BP
def generateBPListSite(path):
    result = []
    listDir = os.listdir(path);
    for BP in listDir:
        result.append(genBP(BP, path));
    a = 0;
    return result;

#Проверка на наличие хотя бы одного БП
def hasBP(path):
    listDir = os.listdir(path)
    for newPath in listDir:
        if (isBP(path+"/"+newPath)):
            return True;
    return False;

#поиск внутреннего фото для папки (доджно иметь такое же название)
def findImage(item, path):
    listDir = os.listdir(path+"/"+item);
    for imageName in listDir:
        if (".jpg" in imageName or ".png" in imageName) and item in imageName:
            return "/image/"+path+"/"+item+"/"+imageName;
    return None;

#генерирует узел, внутри которого БП-ы
def generateBP(name, path):
    urlImage = findImage(name,path);
    listSite = generateBPListSite(path+"/"+name);
    result = {
       "ispoccess": True,
       "name": name,
       "urlImage": urlImage,
       "listSite" : listSite
        }
    return result;

#Генерирует узел, которые не является БП
def generateNBP(name, path):
    tempList = [];
    item = {
        "ispoccess": False,
        "name": name,
        "urlImage": findImage(name,path),
        "listSite": generateJSON(path+"/"+name, tempList)
        }
    return item;

#определения типа вложенных папок (пка имеет БП или нет)
def generateJSON(path,iList):

    listDir = os.listdir(path)
    for item in listDir:
        if(hasBP(path+"/"+item)):
            iList.append(generateBP(item, path))
        else:
            iList.append(generateNBP(item, path))
    return iList;

#начало построения дерева алгоритмом обхода в глубину 
@app.route('/dir/<path>')
def get_path(path):
    json = []
    result = generateJSON(path,json)
    return jsonify(result)


#отправка изображения по запросу
@app.route('/image/<path:filename>')
def get_image(filename):

    return send_file(filename, mimetype = 'image/gif');

#сохранение изображения по запросу
@app.route('/imageset/<path:filePath>', methods=['GET', 'POST'])
def set_image(filePath):
    path = "";
    now = datetime.now()    
    d1 = now.strftime("%d.%m.%Y %H.%M.%S")
    for filename in request.files:
        file = request.files[filename]
        fileStorage = file.filename
        
        path = "root/"+filePath+"/"+d1
        if not (os.path.exists(path)):
            os.makedirs(path)
        file.save(os.path.join(path, fileStorage))
    descr = request.form['description']
    with open(os.path.join(path, "description.txt"), 'w') as f:
        f.write(descr);

    return 'file uploaded successfully'

if __name__ == '__main__':
    app.run(host='0.0.0.0')