using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneController : MonoBehaviour
{
    //public Request Request;
    Rigidbody DR;
    public float fixedDistance = 10f;
    private Quaternion targetRotation;
    public string whatTouched;
    private float waitSecond;
    //public JSONpy toPython;

    void Awake(){
        DR = GetComponent<Rigidbody>();
        // if (Request == null)
        // {
        //     Request = FindObjectOfType<Request>();
        // }
    }
    void Start(){
        StartCoroutine(ActionCheck());
    }
    // void Move(){
    //     if(velocity != tempVelocity){
    //         velocity = tempVelocity;
    //     }
    //     botRigid.MovePosition(botRigid.position + transform.forward);
    // }

    void ActionHandler(){
        //Request.SendDataToServer(toPython, HandleServerResponse);
    }

    void HandleServerResponse(string response){
        if(string.IsNullOrEmpty(response)){
            Debug.LogError("Failed to receive a valid response from the server.");
            return;
        }
        // switch(response){
        //     case "move":
        //         Move();
        //         break;
        //     case "grab":
        //     case "drop":
        //     case "turn":
        //         // velocity = 0;
        //         // ClampPosition();
        //         if(response == "turn"){
        //             Turn();
        //         }else if(response == "grab"){
        //             Grab();
        //         }else if(response == "drop"){
        //             Drop();
        //         }
        //         break;
        // }
        
    }
    IEnumerator ActionCheck(){
        while(true){
            ActionHandler();
            yield return new WaitForSeconds(0.1f);
        }
    }
    void Turn(){
        float currentYRotation = transform.eulerAngles.y;
        Quaternion targetRotation = Quaternion.Euler(0, currentYRotation + 90f, 0);

        transform.rotation = targetRotation;
        //botRigid.rotation = targetRotation;

        // ClampRotation();
        // ClampPosition();
    }
}
