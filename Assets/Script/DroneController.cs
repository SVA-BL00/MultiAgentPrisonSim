using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneController : MonoBehaviour
{
    Rigidbody DR;
    public CameraDetector detector;
    public List<GameObject> cameras;
    public float fixedDistance = 0.0001f;
    public float actionDuration = 0.1f;
    public float moveSpeed = 0.1f;
    public float rotationSpeed = 90f;
    private Quaternion targetRotation;
    private Vector3 targetPosition;
    public string whatTouched;
    private string currentAction = null;
    public string isPrisonerInView = "0";

    void Awake()
    {
        DR = GetComponent<Rigidbody>();
    }

    void Start()
    {
        StartCoroutine(ActionCheck());
    }

    void Update()
    {
        if(detector.isDetected){
            isPrisonerInView = "Prisoner";
        }
        if (currentAction != null)
        {
            if (currentAction == "move")
            {
                transform.position = Vector3.MoveTowards(transform.position, targetPosition, moveSpeed * Time.deltaTime);
                if (transform.position == targetPosition)
                {
                    currentAction = null;
                }
            }
            else if (currentAction.StartsWith("turn"))
            {
                transform.rotation = targetRotation;
                if (transform.rotation == targetRotation)
                {
                    currentAction = null;
                }
            }
        }
    }

    public void ActionHandler(string command)
    {
        currentAction = command;

        switch (command)
        {
            case "move":
                Vector3 newPosition = DR.transform.position - transform.forward * 10f;
                targetPosition = newPosition;
                break;

            case "turnN":
                Quaternion turnNorth = Quaternion.Euler(0, 0, 0);
                targetRotation = turnNorth;
                break;

            case "turnS":
                Quaternion turnSouth = Quaternion.Euler(0, 180, 0);
                targetRotation = turnSouth;
                break;

            case "turnE":
                Quaternion turnEast = Quaternion.Euler(0, 90, 0);
                targetRotation = turnEast;
                break;

            case "turnW":
                Quaternion turnWest = Quaternion.Euler(0, 270, 0);
                targetRotation = turnWest;
                break;
            
            case "idle":
                DR.velocity = Vector3.zero;
                DR.angularVelocity = Vector3.zero;
                targetPosition = transform.position;
                targetRotation = transform.rotation;
                break;
                
            case "lower":
                targetPosition = new Vector3(
                    DR.transform.position.x, 
                    DR.transform.position.y - 0.5f, 
                    DR.transform.position.z
                );
                break;

            default:
                Debug.Log("Unknown command received: " + command);
                break;
        }
    }

    void SendEnvironment()
    {
        Vector3 position = DR.transform.position;
        string environmentData = $"{{\"position\": \"{position}\", " +
                                 $"\"cv\": \"{isPrisonerInView}\", " +
                                 $"\"Camera1\": \"{cameras[0].GetComponent<CameraDetector>().isDetected}\", " +
                                 $"\"Camera2\": \"{cameras[1].GetComponent<CameraDetector>().isDetected}\", " +
                                 $"\"Camera3\": \"{cameras[2].GetComponent<CameraDetector>().isDetected}\", " +
                                 $"\"Camera4\": \"{cameras[3].GetComponent<CameraDetector>().isDetected}\"}}";
        FindObjectOfType<Client>().socket.Emit("drone_handler", environmentData);
    }

    IEnumerator ActionCheck()
    {
        while (true)
        {
            SendEnvironment();
            yield return new WaitForSeconds(0.3f);
        }
    }

    void OnCollisionEnter(Collision collision){
        DR.isKinematic = true;
    }
}
