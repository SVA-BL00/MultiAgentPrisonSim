using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneController : MonoBehaviour
{
    Rigidbody DR;
    public List<GameObject> cameras;
    public float fixedDistance = 10f;
    public float actionDuration = 0.1f;
    public float moveSpeed = 5f;
    public float rotationSpeed = 90f;
    private Quaternion targetRotation;
    private Vector3 targetPosition;
    public string whatTouched;
    private string currentAction = null;
    public bool isPrisonerInView;

    void Awake(){
        DR = GetComponent<Rigidbody>();
    }

    void Start(){
        StartCoroutine(ActionCheck());
    }

    void Update(){
        if(currentAction != null){
            if(currentAction == "move"){
                transform.position = Vector3.MoveTowards(transform.position, targetPosition, moveSpeed * Time.deltaTime);
                if (transform.position == targetPosition){
                    currentAction = null;
                }
            }else if(currentAction.StartsWith("turn")){
                transform.rotation = Quaternion.RotateTowards(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
                if(transform.rotation == targetRotation){
                    currentAction = null;
                }
            }
        }
    }

    public void ActionHandler(string command){
        currentAction = command;

        switch(command){
            case "move":
                Vector3 newPosition = DR.transform.position + Vector3.forward * 10f;
                targetPosition = newPosition;
                break;

            case "turnN":
                Quaternion turnNorth = Quaternion.Euler(0, 180, 0);
                targetRotation = turnNorth;
                break;

            case "turnS":
                Quaternion turnSouth = Quaternion.Euler(0, -90, 0);
                targetRotation = turnSouth;
                break;

            case "turnE":
                Quaternion turnEast = Quaternion.Euler(0, 270, 0);
                targetRotation = turnEast;
                break;

            case "turnW":
                Quaternion turnWest = Quaternion.Euler(0, 90, 0);
                targetRotation = turnWest;
                break;

            default:
                Debug.Log("Unknown command received: " + command);
                break;
        }
    }

    void SendEnvironment(){
        // TODO: BOOL VISION COMPUTACIONAL
        Vector3 position = DR.transform.position;
        string environmentData = $"{{\"position\": \"{DR.transform.position}\", " +
                                 $"\"cv\": \"{isPrisonerInView}\", " +
                                 $"\"Camera1\": \"{cameras[0].GetComponent<CameraDetector>().isDetected}\", " +
                                 $"\"Camera2\": \"{cameras[1].GetComponent<CameraDetector>().isDetected}\", " +
                                 $"\"Camera3\": \"{cameras[2].GetComponent<CameraDetector>().isDetected}\", " +
                                 $"\"Camera4\": \"{cameras[3].GetComponent<CameraDetector>().isDetected}\"}}";
        FindObjectOfType<Client>().socket.Emit("drone_handler", environmentData);
    }

    IEnumerator ActionCheck(){
        while (true){
            SendEnvironment();
            yield return new WaitForSeconds(0.3f);
        }
    }
}
