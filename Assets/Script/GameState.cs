using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameState : MonoBehaviour
{
    public Client clientScript;

    void Start(){
        StartGame();
    }
    public async void StartGame(){
        //Debug.Log("StartGame called");
        await clientScript.StartGameSession();
    }

    public async void EndGame(){
        await clientScript.EndGameSession();
    }
}
