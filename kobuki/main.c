/* FIXME: Verify correct myRIO macros are set in project settings */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <inttypes.h>

#include "myrio/UART.h"
#include "myrio/visa.h"
#include "kobukiDriver/kobukiSensorPoll.h"
#include "kobukiDriver/kobukiActuator.h"

#include "myrio/MyRio.h"
#include "myrio/Accelerometer.h"
#include "kobukiNavigationStatechart.h"
//#include "DIO.h"
#define BaudRate 115200
#define DataBit 8

/* Function prototypes */
uint64_t getTimeInMs(void);
void delayMs(const uint64_t msDelay);
void waitUntilNextMsMultiple(const uint64_t msMultiple);
int32_t openUART(MyRio_Uart * uart);
extern NiFpga_Session myrio_session; // this is global session . It is useful to do low level hardware.
/* IO settings */


/* program parameters */
const int32_t driveDistance = 200;		/* distance to drive, in mm */
const int32_t turnAngle = 90;			/* angle to turn, in mm */
const int16_t WHEEL_SPEED = 200;		/* maximum speed to turn the wheels, in mm/s */
const double  accelSmoothing = 0.1;		/* accelerometer smoothing coefficient */
int32_t normalized180(int32_t a){
    a = (a + 180)%360;
    if (a < 0)
        a += 360;
    return a - 180;
}
int main(int argc, char **argv){
	NiFpga_Status status = 0;

	int32_t drive_status = 0;

	MyRio_Uart uart;
    uart.name = "ASRL2::INSTR";
    uart.defaultRM = 0;
    uart.session = 0;
	status = openUART(&uart);
	Uart_Clear(&uart);



	int16_t                 radius = 0;
	int16_t                 speed = 0;

	/*
	 * Open the myRIO NiFpga Session.
	 * This function MUST be called before all other functions. After this call
	 * is complete the myRIO target will be ready to be used.
	 */
	status = MyRio_Open();

	int iter = 0;
	NiFpga_WriteU8 (myrio_session , DOLED30 , 0x0);
	while(!NiFpga_IsError(status)){
		if(iter % 16 == 0) {
			NiFpga_WriteU8 (myrio_session , DOLED30 , 0x01);
			KobukiNavigationStatechart(WHEEL_SPEED,&radius,&speed,&uart);
			NiFpga_WriteU8 (myrio_session , DOLED30 , 0x00);
			printf("Driving with speeds %d %d\n", radius, speed);
		}

		drive_status = kobukiDriveRadius(&uart, radius, speed);
		if (drive_status < VI_SUCCESS){
			printf("Drive command failed with status %d\n", drive_status);
			return -1;
		}
		waitUntilNextMsMultiple(60);
		iter += 1;
	}

	return status;
}

/* system time, in ms */
uint64_t getTimeInMs(void){
	struct timeval tv;
	gettimeofday(&tv, NULL);
	return (tv.tv_sec) * 1000 + (tv.tv_usec) / 1000;
}

/* delay a fixed number of ms */
void delayMs(const uint64_t msDelay){
	usleep(msDelay * 1000);
}

/* loop timing - wait until system clock is modulo ms */
void waitUntilNextMsMultiple(const uint64_t msMultiple){
	const uint64_t msCounter = getTimeInMs() % msMultiple;
	if(msCounter > 0){
		delayMs(msMultiple - msCounter);	/* delay modulo difference */
	}
}


int32_t openUART(MyRio_Uart * p_uart){
    int32_t status = 0;
	status = Uart_Open(p_uart, BaudRate, DataBit,
                       Uart_StopBits1_0, Uart_ParityNone);
    if (status < VI_SUCCESS)
    {
    	printf("Open failed\n");
    }
    return status;
}
