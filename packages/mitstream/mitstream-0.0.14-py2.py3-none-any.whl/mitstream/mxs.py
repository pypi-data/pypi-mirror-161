
import pandas as pd



def AddSectors(mx, lookup, o='O', d='D', z='Zone', s='Sector'):
    '''
    inputs:
            mx:
                Type: Dataframe
                Desc.: matrix to add sectors info to
                
            lookup:
                Type: dataframe
                Desc.: Sectors lookup
            
            o:
                Type: string
                Desc.: name of origin/production zone field in the matrix
            
            d:
                Type: string
                Desc.: name of destination/attraction zone field in the matrix
                
            z:
                Type: string
                Desc.: name of the zone field in the lookup
                
            s:
                Type: string
                Desc.: name of sector field in the lookup
                
    function:
        adds sector info for origin/destination or production attraction matrix 
        
    outputs:
        mx:
            Type: Dataframe
            Desc.: matrix with added sector info
    '''
    #get all current columns in the matrix 
    #get mx headers
    lHeaders = list(mx.columns)
    #merge mx to lookup on origin/production
    mx = mx.merge(lookup, how='left', left_on=[o], right_on=[z])
    #rename columns
    mx = mx.rename(columns={s: o+'_Sector'})
    #merge mx to lookup on destination/attraction
    mx = mx.merge(lookup, how='left', left_on=[d], right_on=[z])
    #rename columns
    mx = mx.rename(columns={s: d+'_Sector'})
    #adjust headers list
    nHeaders = lHeaders + [o+'_Sector', d+'_Sector']
    #keep needed column
    mx = mx[nHeaders]
    
    return mx
