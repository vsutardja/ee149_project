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
	unsigned int clilen;
	struct sockaddr_in serv_addr, cli_addr;
	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(DEFAULT_PORT);
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (socket < 0) {
		perror("error opening socket");
	    exit(1);
	}

	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
		perror("error binding");
		exit(2);
	}
	printf("waiting for client connection on port %d\n", DEFAULT_PORT);
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
	int16_t * const 			pRadius,
	int16_t * const 			pSpeed,
	MyRio_Uart *				uart_p
	){
	if (sockfd < 0) {
		printf("Driving\n");
		kobukiDriveRadius(uart_p, 0, 0);
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
			printf("connection closed\n");
			exit(4);
		}
		printf("message received: %s\n", buffer);

		parseSpeeds(buffer, speeds);
	} else {
		printf("No data. Using old values %d %d\n", speeds[0], speeds[1]);
	}
	printf("speeds: %d %d\n", speeds[0], speeds[1]);
	*pRadius = speeds[0];
	*pSpeed = speeds[1];
}
