using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneController : MonoBehaviour
{
    //public Request Request;
    Rigidbody DR;
    public float fixedDistance = 10f;
    public float actionDuration = 0.1f;
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
        //StartCoroutine(Move());
        //StartCoroutine(Turn());
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
    IEnumerator Turn(){
        float elapsedTime = 0f;

        Quaternion qcurrentYRotation = transform.rotation;
        float currentYRotation = transform.eulerAngles.y; // Needed to obtain target, same as qcurrent

        Quaternion targetRotation = Quaternion.Euler(0, currentYRotation + 90f, 0);

        while (elapsedTime < actionDuration){
            transform.rotation = Quaternion.Slerp(qcurrentYRotation, targetRotation, elapsedTime / actionDuration);
            elapsedTime += Time.deltaTime;
            yield return null;
        }

        transform.rotation = targetRotation;
    }

    IEnumerator Move(){
        float elapsedTime = 0f;
        Vector3 startingPos = transform.position;
        Vector3 targetPos = startingPos - transform.forward * 10f;

        while (elapsedTime < actionDuration){
            DR.MovePosition(Vector3.Lerp(startingPos, targetPos, elapsedTime / actionDuration));
            elapsedTime += Time.deltaTime;
            yield return null;
        }

        DR.MovePosition(targetPos);
    }
}
