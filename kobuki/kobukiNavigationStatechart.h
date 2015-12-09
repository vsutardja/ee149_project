/*
 * irobotNavigationStatechart.h
 *
 *  Created on: Mar 7, 2013
 *      Author: jjensen
 */

#ifndef IROBOTNAVIGATIONSTATECHART_H_
#define IROBOTNAVIGATIONSTATECHART_H_


#include "kobukiDriver/kobukiSensorTypes.h"
#include "myrio/Accelerometer.h"
#include "sys/socket.h"
#include "sys/types.h"
#include <sys/select.h>
#include "netinet/in.h"
#include <netdb.h>
#include <string.h>
#include <sys/fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include "myrio/UART.h"
#include "kobukiDriver/kobukiActuator.h"

/* accelerometer */

void KobukiNavigationStatechart(
	const int16_t 				maxWheelSpeed,
	int16_t * const 			pRadius,
	int16_t * const 			pSpeed,
	MyRio_Uart *				uart_p
);

#endif /* IROBOTNAVIGATIONSTATECHART_H_ */
