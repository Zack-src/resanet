#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

def convertirDateISOversFR( dateISO ) :
	print ('[START] dateResanet::convertirDateISOversFR()')
	annee , mois , jour = dateISO.split( '-' )
	dateFR = '/'.join( ( jour , mois , annee ) )
	print ('[STOP] dateResanet::convertirDateISOversFR()')
	return dateFR
	
def convertirDateFRversISO( dateFR ) :
	print ('[START] dateResanet::convertirDateFRversISO()')
	jour , mois , annee = dateFR.split( '/' )
	dateISO = '-'.join( ( annee , mois , jour ) )
	print ('[STOP] dateResanet::convertirDateFRversISO()')
	return dateISO	
	
def getDateAujourdhuiFR() :
	dateCourante = datetime.datetime.today()
	aujourdhui = '%02d/%02d/%04d' % ( dateCourante.day , dateCourante.month , dateCourante.year )
	return aujourdhui
	
def getDateAujourdhuiISO() :
	dateCourante = datetime.datetime.today()
	aujourdhui = '%04d-%02d-%02d' % ( dateCourante.year , dateCourante.month , dateCourante.day )
	return aujourdhui
	
def getDatesPeriodeCouranteISO() :
	print ('[START] dateResanet::getDatesPeriodeCouranteISO()')

	dates = []
	
	dateAujourdhui= datetime.datetime.today()
	numJourAujourdhui = dateAujourdhui.weekday()
	
	dateCourante = dateAujourdhui - datetime.timedelta( numJourAujourdhui )
	
	for i in range( 12 ) :
		if i != 5 and i != 6 :
			dateISO = '%04d-%02d-%02d' % ( dateCourante.year , dateCourante.month , dateCourante.day )
			dates.append( dateISO )
			
		dateCourante = dateCourante + datetime.timedelta( 1 )

	print ('[STOP] dateResanet::getDatesPeriodeCouranteISO()')	 
	return dates

import locale
locale.setlocale(locale.LC_TIME, '')

def ConvertDateToDateName( date ):
	cr_date = datetime.datetime.strptime(date, '%Y-%m-%d')
	return cr_date.strftime("%A")


def getDatesPeriodeCouranteFR():
	dates = []

	dateAujourdhui = datetime.datetime.today()
	numJourAujourdhui = dateAujourdhui.weekday()

	dateCourante = dateAujourdhui - datetime.timedelta(numJourAujourdhui)

	for i in range(12):
		if i != 5 and i != 6:
			dateFR = '%02d/%02d/%04d' % (dateCourante.day, dateCourante.month, dateCourante.year)
			dates.append(dateFR)

		dateCourante = dateCourante + datetime.timedelta(1)

	return dates

if __name__ == '__main__' :
	print (convertirDateUSversFR( '2017-02-01' ))
	print (convertirDateFRversUS( '01/02/2017' ))
	print (getDateAujourdhuiFR())
	print (getDateAujourdhuiUS())
	
	dates = getDatesPeriodeCouranteUS()
	for uneDate in dates :
		print (uneDate)
