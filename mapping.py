#mapping function for main
#last update 03/04/23

import folium

def mapping(aircraft):


    print("inside mapping")
    test_lat = 43.08488748841366 
    test_long = 15.163225446428571

    ohio_lat = 39.3292
    ohio_long = -82.1013

    map = folium.Map(location=[test_lat, test_long]) 

    for plane in aircraft:
        print("\nID:", hex(int(plane.ID,2)))
        lat_list = plane.lat
        long_list =plane.long
        alt_list = plane.alt
        heading_list = plane.heading
        vel_list = plane.vel
        #, icon=folium.DivIcon(html=html)

        html=f"""
        <div><svg>
            <circle cx="50" cy="50" r="40" fill="#69b3a2" opacity=".4"/>
            <rect x="35", y="35" width="30" height="30", fill="red", opacity=".3" 
            </svg>
            <p> pls work</p>
        </div>
        """

        for i in range(len(lat_list)):

            folium.Marker(
                [float(lat_list[i]), float(long_list[i])], popup="<i>Athens</i>", icon=folium.DivIcon(html=html)
            ).add_to(map)
        


    map.save("disp_map.html")

                                           
