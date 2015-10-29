/*
* KobukiNavigationStatechart.c
*
*/

#include "kobukiNavigationStatechart.h"
#include <math.h>
#include <stdlib.h>

int sockfd = -1;
int newsockfd = -1;
int speeds[2] = {0, 0};

// Program States
typedef enum{
	INITIAL = 0,						// Initial state
	PAUSE_WAIT_BUTTON_RELEASE,			// Paused; pause button pressed down, wait until released before detecting next press
	UNPAUSE_WAIT_BUTTON_PRESS,			// Paused; wait for pause button to be pressed
	UNPAUSE_WAIT_BUTTON_RELEASE,		// Paused; pause button pressed down, wait until released before returning to previous state
	DRIVE,								// Drive straight
	TURN								/// Turn

} robotState_t;

#define DEG_PER_RAD			(180.0 / M_PI)		// degrees per radian
#define RAD_PER_DEG			(M_PI / 180.0)		// radians per degree
#define LEN                 (16)
#define DEFAULT_PORT        (1234)

void initializeSocket() {
	int clilen;
	struct sockaddr_in serv_addr, cli_addr;
	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(DEFAULT_PORT);
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (socket < 0) {
		perror("error opening socket");
	    exit(1);
	} else {
		printf("%s\n", "hi");
	}

	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
		perror("error binding");
		exit(2);
	}
	printf("waiting for client connection\n");
	listen(sockfd, 5);
	clilen = sizeof(cli_addr);
	newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
	printf("connection established\n");
}

void parseSpeeds(char *buf, int *speeds) {
	char *end;
	speeds[0] = (int) strtol(buf, &end, 10);
	speeds[1] = (int) strtol(end, NULL, 10);
}

void KobukiNavigationStatechart(
	const int16_t 				maxWheelSpeed,
	const int32_t 				netDistance,
	const int32_t 				netAngle,
	const KobukiSensors_t		sensors,
	const accelerometer_t		accelAxes,
	int16_t * const 			pRightWheelSpeed,
	int16_t * const 			pLeftWheelSpeed,
	const bool					isSimulator
	){
	if (sockfd < 0) {
		initializeSocket();
	}
	fd_set rfds;
	struct timeval tv;
	int n, retval;
	char buffer[LEN];
	FD_ZERO(&rfds);
	FD_SET(newsockfd, &rfds);
	tv.tv_sec = 0;
	tv.tv_usec = 1000000;
	printf("polling...\n");
	retval = select(newsockfd+1, &rfds, NULL, NULL, &tv);
	printf("done polling\n");
	if (retval == -1) {
		perror("select");
		exit(5);
	} else if (retval > 0 && FD_ISSET(newsockfd, &rfds)) {
		bzero(buffer, LEN);
		n = read(newsockfd, buffer, LEN - 1);
		if (n < 0) {
			perror("error reading from socket");
			exit(3);
		} else if (n == 0) {
			perror("nothing");
			exit(4);
		}
		printf("message received: %s\n", buffer);

		parseSpeeds(buffer, speeds);
	} else {
		printf("No data. Using old values %d %d\n", speeds[0], speeds[1]);
	}
	printf("speeds: %d %d\n", speeds[0], speeds[1]);
	*pLeftWheelSpeed = speeds[0];
	*pRightWheelSpeed = speeds[1];

	// local state
	static robotState_t 		state = DRIVE;				// current program state
	static robotState_t			unpausedState = DRIVE;			// state history for pause region
	static int32_t				distanceAtManeuverStart = 0;	// distance robot had travelled when a maneuver begins, in mm
	static int32_t				angleAtManeuverStart = 0;		// angle through which the robot had turned when a maneuver begins, in deg

	// outputs
	int16_t						leftWheelSpeed = 0;				// speed of the left wheel, in mm/s
	int16_t						rightWheelSpeed = 0;			// speed of the right wheel, in mm/s

	//*****************************************************
	// state data - process inputs                        *
	//*****************************************************


     printf("checking state\n");
	 if (state == INITIAL
		|| state == PAUSE_WAIT_BUTTON_RELEASE
		|| state == UNPAUSE_WAIT_BUTTON_PRESS
		|| state == UNPAUSE_WAIT_BUTTON_RELEASE
		|| sensors.buttons.B0				// pause button
		){
		switch (state){
		case INITIAL:
			// set state data that may change between simulation and real-world
			if (isSimulator){
			}
			else{
			}
			state = UNPAUSE_WAIT_BUTTON_PRESS; // place into pause state
			break;
		case PAUSE_WAIT_BUTTON_RELEASE:
			// remain in this state until released before detecting next press
			if (!sensors.buttons.B0){
				state = UNPAUSE_WAIT_BUTTON_PRESS;
			}
			break;
		case UNPAUSE_WAIT_BUTTON_RELEASE:
			// user pressed 'pause' button to return to previous state
			if (!sensors.buttons.B0){
				state = unpausedState;
			}
			break;
		case UNPAUSE_WAIT_BUTTON_PRESS:
			// remain in this state until user presses 'pause' button
			if (sensors.buttons.B0){
				state = UNPAUSE_WAIT_BUTTON_RELEASE;
			}
			break;
		default:
			// must be in run region, and pause button has been pressed
			unpausedState = state;
			state = PAUSE_WAIT_BUTTON_RELEASE;
			break;
		}
	}
	//*************************************
	// state transition - run region      *
	//*************************************
//	else if (state == DRIVE && abs(netDistance - distanceAtManeuverStart) >= 250){
//		angleAtManeuverStart = netAngle;
//		distanceAtManeuverStart = netDistance;
//		state = TURN;
//	}
//	else if (state == TURN && abs(netAngle - angleAtManeuverStart) >= 90){
//		angleAtManeuverStart = netAngle;
//		distanceAtManeuverStart = netDistance;
//		state = DRIVE;
//	}
	// else, no transitions are taken

	//*****************
	//* state actions *
	//*****************
	printf("About to perform action\n");
	switch (state){
	case INITIAL:
	case PAUSE_WAIT_BUTTON_RELEASE:
	case UNPAUSE_WAIT_BUTTON_PRESS:
	case UNPAUSE_WAIT_BUTTON_RELEASE:
		// in pause mode, robot should be stopped
		leftWheelSpeed = rightWheelSpeed = 0;
		break;

	case DRIVE:
		// full speed ahead!
		//leftWheelSpeed = rightWheelSpeed = 200;
		printf("In drive\n");
		leftWheelSpeed = speeds[0];
		rightWheelSpeed = speeds[1];
		break;

	case TURN:
		leftWheelSpeed = 100;
		rightWheelSpeed = -leftWheelSpeed;
		break;

	default:
		// Unknown state
		leftWheelSpeed = rightWheelSpeed = 0;
		break;
	}


	*pLeftWheelSpeed = leftWheelSpeed;
	*pRightWheelSpeed = rightWheelSpeed;
}
