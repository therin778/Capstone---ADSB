#mapping function for main
#last update 03/05/23

import folium

show_trail = True  #Set to True to show trail

def mapping(aircraft):


    print("inside mapping")
    test_lat =  37.066707287804554
    test_long = 13.802470331606658

    ohio_lat = 39.3292
    ohio_long = -82.1013

    map = folium.Map(location=[test_lat, test_long], )

    print(len(aircraft)) 

    for plane in aircraft:

        coord_pair = []
        map_finished = False

        plane_list = str(hex(int(plane.ID,2)))
        lat_list = plane.lat
        long_list =plane.long
        alt_list = plane.alt
        heading_list = plane.heading
        vel_list = plane.vel
        print("plane_list: ", plane_list)


        for i in range(len(lat_list)):

            message = plane_list


            html=f"""
                <div>
            
                    <svg height="200" width="200">
                        <rect x="10" y="10" width="110" height="50"
                        style="fill:white;stroke:black;stroke-width:2;opacity:0.5" />
                        <text fill="black" font-size="12" font-family="Verdana" x="15" y="30">ICAO: {message}</text>
                    </svg>
                </div>
            """

            folium.Marker(
                [float(lat_list[i]), float(long_list[i])], icon=folium.DivIcon(html=html)
            ).add_to(map)
        
            folium.Marker(
                [float(lat_list[i]), float(long_list[i])], popup="<i>Athens</i>"
            ).add_to(map)

            coord_pair.append([float(lat_list[i]), float(long_list[i])])
            map_finished = True

        if map_finished == True:
            if show_trail == True:
                folium.PolyLine(locations = coord_pair,
                        color='blue',
                        weight=2,
                        opacity=1,
                        dash_array=[10, 5]).add_to(map)

    map.save("disp_map.html")
