#!/usr/bin/python
# -*- coding: utf-8 -*-

from pickle import NONE
from flask import *
from modeles import modeleResanet
from technique import datesResanet
from datetime import datetime

app = Flask( __name__ )
app.secret_key = 'resanet'

@app.route('/')
def index() :
	code = request.args.get("code")
	return render_template( 'vueAccueil.html', error = code)

@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


##########################################################################
#USAGER
##########################################################################

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				session[ 'role' ] = "usager"

				return redirect( '/usager/reservations/lister' )
			else :
				return redirect( '/?code=1')
		else :
			return redirect( '/?code=2')
	else :
		return redirect( '/?code=3')

@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	session.pop( 'mdp' , None )
	session.pop( 'role' , None )
	return redirect( '/' )

@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations() :
	print ('[START] appResanet::listerReservation()')
	
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	
	solde = '%.2f' % ( soldeCarte , )

	aujourdhui = datesResanet.getDateAujourdhuiISO()
	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	JoursFerier = modeleResanet.getJourFerier()
	dates = []
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )

		uneDate[ 'verrouillee' ] = False		
		if uneDateISO <= aujourdhui :
			uneDate[ 'verrouillee' ] = True
		
		uneDate[ 'reservee' ] = False
		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
			
		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True
	
		uneDate[ 'ferier' ] = False
		for i in range(len(JoursFerier)):
			if JoursFerier[i]['date'] == uneDate[ 'iso' ] and JoursFerier[i]['activee'] == 1:
				uneDate[ 'ferier' ] = True

		dates.append( uneDate )

	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False
		
	DateName = []
	for i in range(len(dates)):
		DateName.append(datesResanet.ConvertDateToDateName( dates[i]['iso'] ))
		
	print ('[STOP] appResanet::listerReservation()')
	
	return render_template( 'vueListeReservations.html' , 
		DayName = DateName, laSession = session , leSolde = solde , 
		lesDates = dates , soldeInsuffisant = soldeInsuffisant)


@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )




##########################################################################
#GESTIONNAIRE
##########################################################################

def sessionGestionnaire():
	if "role" in session:
		if session[ 'role' ] == "gestionnaire":
			return True
	return False


@app.route( '/gestionnaire/seConnecter' , methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	login = request.form[ 'login' ]
	mdp = request.form[ 'mdp' ]

	if login != '' and mdp != '' :
		gestionnaire = modeleResanet.seConnecterGestionnaire( login , mdp )
		if gestionnaire == None:
			print("db innacessible")
		if len(gestionnaire) != 0 :
			session[ 'nom' ] = gestionnaire[ 'nom' ]
			session[ 'prenom' ] = gestionnaire[ 'prenom' ]
			session[ 'mdp' ] = mdp
			session[ 'role' ] = "gestionnaire"

			return redirect( '/gestionnaire/getPersonnelAvecCarte' )
		else :
			return redirect( '/?code=2')
	else :
		return redirect( '/?code=3')

@app.route( '/gestionnaire/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterGestionnaire() :
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	session.pop( 'mdp' , None )
	session.pop( 'role' , None )
	return redirect( '/' )

@app.route( '/gestionnaire/getPersonnelAvecCarte' , methods = [ 'GET' ] )
def getPersonnelAvecCarte() :
	if sessionGestionnaire():
		personnels = modeleResanet.getPersonnelsAvecCarte()
		if personnels != None :
			datesHistorique = []
			for i in range(len(personnels)):
				uneDate = {}
				uneDate[ 'dates' ] = modeleResanet.getHistoriqueReservationsCarte(personnels[i]['matricule'])
				datesHistorique.append(uneDate)

			return render_template('vuePersonnelAvecCarte.html', lePersonnels = personnels, dates = datesHistorique)
		else :
			print("db innacessible")
	else:
		return redirect('/')

@app.route( '/gestionnaire/reinitialiserMdp/<numeroCarte>' , methods = [ 'GET' ] )
def reinitialiserMdp(numeroCarte) :
	if sessionGestionnaire():
		modeleResanet.reinitialiserMdp(numeroCarte)
		return redirect( '/gestionnaire/getPersonnelAvecCarte' )
	else:
		return redirect('/')

@app.route( '/gestionnaire/activerCarte/<numeroCarte>' , methods = [ 'GET' ] )
def activerCarte(numeroCarte) :
	if sessionGestionnaire():
		modeleResanet.activerCarte(numeroCarte)
		return redirect( '/gestionnaire/getPersonnelAvecCarte' )
	else:
		return redirect('/')

@app.route( '/gestionnaire/bloquerCarte/<numeroCarte>' , methods = [ 'GET' ] )
def bloquerCarte(numeroCarte) :
	if sessionGestionnaire():
		modeleResanet.bloquerCarte(numeroCarte)
		return redirect( '/gestionnaire/getPersonnelAvecCarte' )
	else:
		return redirect('/')

@app.route( '/gestionnaire/CrediterCarte/<matricule>' , methods = [ 'POST' ] )
def CrediterCarte(matricule) :
	if sessionGestionnaire():
		somme = request.values.get("somme")
		modeleResanet.crediterCarte(matricule, somme)
		return redirect( '/gestionnaire/getPersonnelAvecCarte' )
	else:
		return redirect('/')

@app.route( '/gestionnaire/CreerCarte/<matricule>' , methods = [ 'POST' ] )
def CreerCarte(matricule):
	if sessionGestionnaire():
		active = False
		if request.form.get( 'active' ) == "on":
			active = True
		
		modeleResanet.creerCarte(matricule, active)
		return redirect( '/gestionnaire/getPersonnelSansCarte' )
	else:
		return redirect('/')

@app.route( '/gestionnaire/SupprimerCarte/<matricule>' , methods = [ 'GET' ] )
def SupprimerCarte(matricule):
	if sessionGestionnaire():
		modeleResanet.supprimerCarte(matricule)
		return redirect( '/gestionnaire/getPersonnelAvecCarte' )
	else:
		return redirect('/')

@app.route( '/gestionnaire/getDateReservation/', methods = [ 'GET' , 'POST' ] )
def getDateReservation() :
	if sessionGestionnaire():
		date = request.values.get('date')
		personnels = []
		if date != 0 :
			personnels = modeleResanet.getReservationsDate(date)

		return render_template( 'vuePersonnelReservation.html', data = personnels, request = "Date")
	else:
		return redirect('/')

@app.route( '/gestionnaire/getCarteReservation/', methods = [ 'GET' , 'POST' ] )
def getPersonnelReservation() :
	if sessionGestionnaire():
		matricule = request.values.get('matricule')
		debut = request.values.get('debut')
		fin = request.values.get('fin')
		date = []
		if matricule != 0 :
			date = modeleResanet.getReservationsCarte(matricule, debut, fin)
			print(date)
		return render_template( 'vuePersonnelReservation.html', data = date, request = "Carte" )
	else:
		return redirect('/')

@app.route( '/gestionnaire/getPersonnelSansCarte' , methods = [ 'GET' ] )
def getPersonnelSansCarte() :
	if sessionGestionnaire():
		personnels = modeleResanet.getPersonnelsSansCarte()
		if personnels != None :
			return render_template('vuePersonnelSansCarte.html', lePersonnels = personnels)
		#else : db inacc??sible
	else:
		return redirect('/')

@app.route( '/gestionnaire/JourFerier' , methods = [ 'GET' ] )
def getJourFerier() :
	if sessionGestionnaire():
		dates = modeleResanet.getJourFerier()
		for i in range(len(dates)):
			print(dates[i])
		if dates != None :
			return render_template('vueJourFerier.html', joursFerier = dates)
		#else : db inacc??sible
	else:
		return redirect('/')

@app.route( '/gestionnaire/addJourFerier', methods = [ 'POST' ])
def addJourFerier():
	if sessionGestionnaire():
		date = request.form[ 'date' ]
		description = request.form[ 'description' ]

		activee = 0
		if request.form.get( 'activee' ) == "on":
			activee = 1

		modeleResanet.addJourFerier(date, description, activee)

		return redirect('/gestionnaire/JourFerier')
	else:
		return redirect('/')

@app.route( '/gestionnaire/removeJourFerier/<jour>', methods = [ 'GET' ])
def removeJourFerier(jour):
	if sessionGestionnaire():
		
		modeleResanet.removeJourFerier(jour)
		return redirect('/gestionnaire/JourFerier')

	else:
		return redirect('/')

@app.route( '/gestionnaire/EnableJourFerier/<jour>', methods = [ 'GET' ])
def EnableJourFerier(jour):
	if sessionGestionnaire():
		print('[START] modeleResanet::EnableJourFerier')
		modeleResanet.EnableJourFerier(jour)
		return redirect('/gestionnaire/JourFerier')

	else:
		return redirect('/')

@app.route( '/gestionnaire/DisableJourFerier/<jour>', methods = [ 'GET' ])
def DisableJourFerier(jour):
	if sessionGestionnaire():
		print('[START] modeleResanet::DisableJourFerier')
		modeleResanet.DisableJourFerier(jour)
		return redirect('/gestionnaire/JourFerier')
	else:
		return redirect('/')

if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )