print 'reloading utils'
import urllib2

# if an except block is run when it shouldn't have been run this function
# it will try and send off the data using a google form that will allow us to try and fix the issue
# called by bugReport(version, traceback.format_exc())

def bugReport(submitThis=None):
	if submitThis is not None:
		try:
			urllib2.urlopen('https://docs.google.com/forms/d/e/1FAIpQLSdho3ivB1ulh8k_p06ZpFl6rhvWIEky5Zn-zewa1xk48ucmzA/viewform?usp=pp_url&entry.1103098740={}&entry.1865363410={}'.format(filter_version,submitThis))
		except:
			pass

	else:
		try:
			urllib2.urlopen('https://docs.google.com/forms/d/e/1FAIpQLSdho3ivB1ulh8k_p06ZpFl6rhvWIEky5Zn-zewa1xk48ucmzA/viewform?usp=pp_url&entry.1103098740={}&entry.1865363410={}'.format(filter_version,traceback.format_exc()))
		except:
			pass