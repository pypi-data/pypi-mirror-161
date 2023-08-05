

#Physical
G_cgs=6.6743015e-8  #gravity constant cgs
G_AUMsunyr = 39.476926408897626 #gravity AU^3/(Msun*yr^2) (astropy: ct.G.to("AU^3/(Msun * yr^2)"))
c_cgs=2.99792458e10 #speed of light cgs (astropy: ct.c.to("cm/s")"))
c_AUyr = 63241.07708426628 #speed of light AU/yr   (astropy: ct.c.to("AU/yr")"))


#Transformation
Msun_to_cgs = 1.988409870698051e+33 #msun/g (astropy: u.Msun.to(u.g))
AU_to_cgs   = 1.495978707e13 #AU/cm (astropy: u.AU.to(u.cm))
Rsun_to_cgs = 6.95700e10 #rsun/cm (astropy: u.Rsun.to(u.cm))
Rsun_to_AU  = Rsun_to_cgs/AU_to_cgs #Rsun/AU (astropy: u.Rsun.to(u.AU))
yr_to_cgs   = 3.1557600e7 #yr/seconds (astropy: u.yr.to(u.s))
yr_to_Myr   =   1e-6    #yr/Myr
cgs_to_yr   = 1/yr_to_cgs
