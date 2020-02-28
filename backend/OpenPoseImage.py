import cv2
import time
import numpy as np
from skimage import io


def computeDepthSide(knee,hip):
        #remember its backwards because 0,0 is top left
        answer = "squatting below parallell"
        if(hip[1]>=knee[1]):
            return answer
        else:
            angle = np.degrees(np.arctan((knee[1]-hip[1])/(hip[0]-knee[0])))
            answer = str(int(angle))
            return answer

def checkBalanceSide(ankle,shoulder,nose):
    difference = (ankle[0] - shoulder[0])
    comparison = np.abs(ankle[1] - nose[1])

    return round(difference/comparison,2)


# MODE = "COCO"
def detectImage(frame):

    # if MODE == "COCO":
    protoFile = "pose/coco/pose_deploy_linevec.prototxt"
    weightsFile = "pose/coco/pose_iter_440000.caffemodel"
    nPoints = 18
    POSE_PAIRS = [ [1,0],[1,2],[1,5],[2,3],[3,4],[5,6],[6,7],[1,8],[8,9],[9,10],[1,11],[11,12],[12,13],[0,14],[0,15],[14,16],[15,17]]

    # elif MODE == "MPI" :
    #     protoFile = "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
    #     weightsFile = "pose/mpi/pose_iter_160000.caffemodel"
    #     nPoints = 15
    #     POSE_PAIRS = [[0,1], [1,2], [2,3], [3,4], [1,5], [5,6], [6,7], [1,14], [14,8], [8,9], [9,10], [14,11], [11,12], [12,13] ]


    #frame = cv2.imread(image)
    frameCopy = np.copy(frame)
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    threshold = 0.1

    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
    t = time.time()
    # input image dimensions for the network
    inWidth = 368
    inHeight = 368
    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                            (0, 0, 0), swapRB=False, crop=False)

    net.setInput(inpBlob)

    output = net.forward()
    print("time taken by network : {:.3f}".format(time.time() - t))

    H = output.shape[2]
    W = output.shape[3]

    # Empty list to store the detected keypoints
    points = []

    for i in range(nPoints):
        # confidence map of corresponding body's part.
        probMap = output[0, i, :, :]

        # Find global maxima of the probMap.
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
        
        # Scale the point to fit on the original image
        x = (frameWidth * point[0]) / W
        y = (frameHeight * point[1]) / H

        if prob > threshold : 
            cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

            # Add the point to the list if the probability is greater than the threshold
            points.append((int(x), int(y)))
        else :
            points.append(None)

    # Draw Skeleton
    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], (0, 255, 255), 2)
            cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

    

    #def checkBackStraight()

    # cv2.imshow('Output-Keypoints', frameCopy)
    # cv2.imshow('Output-Skeleton', frame)


    # cv2.imwrite('Output-Keypoints.jpg', frameCopy)
    # cv2.imwrite('Output-Skeleton.jpg', frame)

    # print("Total time taken : {:.3f}".format(time.time() - t))
    # print("all points",points)
    # print("twelve",points[12])
    # print("nine",points[9])
    # print("13",points[13])

    #checks depth of squat
    print("left angle estimation is",computeDepthSide(points[12],points[11]))
    print("right angle estimation is",computeDepthSide(points[9],points[8]))
    #checks ankle vs shoulder to determine if weight is balanced assuming height is 6ft
    #if positive it means the shoulders are
    print("weight is off balance by approximatly", checkBalanceSide(points[13],points[5],points[0])*60,"inches")
    #cv2.waitKey(0)

#detectImage("squat1.jpg")
