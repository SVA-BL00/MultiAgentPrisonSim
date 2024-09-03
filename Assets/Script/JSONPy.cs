using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

[Serializable]
public struct JSONpy{
    public string ID;
    public string rotation;
    public string resultTuple;
    public bool hasObject;
    public bool isDone;
    public JSONpy(string _ID, string _rotation, string _resultTuple, bool _hasObject, bool _isDone){
        ID = _ID;
        rotation = _rotation;
        resultTuple = _resultTuple;
        hasObject = _hasObject;
        isDone = _isDone;
    }
}