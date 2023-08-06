
import o7lib.util.input
import o7lib.weather.wind_report as wr


#*************************************************
#
#*************************************************
def Menu():

    siteId = 23100
    lon = -71.1948
    lat = 46.8424

    while True :
        print ('-' * 25)
        print ('O7 Weather Menu')
        print (f'Site Id: {siteId}')
        print (f'Lon,Lat: {lon},{lat}')
        print ('-' * 25)
        print ('1 - Wind Report HTML')
        print ('-' * 25)

        t, key = o7lib.util.input.InputMulti('Option: Exit(e), Selection(int)')
        if t == 'str' and key.lower() == 'e':
            break
        if t == 'int':
            if key == 1:
                wr.WindReportHtml(lon, lat, siteId )


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    Menu()
