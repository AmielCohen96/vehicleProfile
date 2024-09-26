from create_file_process import create_file
from vehicle_profiles import VehicleProfiles


def main():

    vehicle_profiles = VehicleProfiles()



    #start the process of creating the file
    create_file()

    print(vehicle_profiles.profiles is not None)





if __name__ == "__main__":
    main()