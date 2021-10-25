import requests
import webbrowser
import json
import pandas as pd
from datetime import datetime

jedicavebros0000 = '{"email":"jedicavebros@gmail.com", ' \
                   '"lastmaxed":"1634704756.3000295",' \
                   '"password":"secrldrasterls1",' \
                   '"clientSecret":"5f70bc1fab8a57d286aa98b9bf375b3d8971e1e1",' \
                   '"refreshToken":"3eda2676ef9d1e0bf1a8e2c6db980bbb01b5a6cf"}'

jedicavebros0001 = '{"email":"jedicavebros0001@gmail.com", ' \
                   '"lastmaxed":"1634706640.355676",' \
                   '"password":"secrldrasterls1",' \
                   '"clientSecret":"a6ec91cb7cf1ba167af25945671c3ecfd1422b69",' \
                   '"refreshToken":"7c17702e1cccd6786b139c963a7bd9ffac9ca80f"}'


jedicavebros0002 = '{"email":"jedicavebro0002@gmail.com", ' \
                   '"lastmaxed":"1634706967.8693378",' \
                   '"password":"secrldrasterls1",' \
                   '"clientSecret":"",' \
                   '"refreshToken":""}'



# never needs to be called again
def initDF():
    df = pd.DataFrame(columns=["email", "clientId", "password", "clientSecret", "refreshToken", "accessToken", "expireIn"])
    df.loc[len(df.index)] = ["jedicavebros@gmail.com","73426","secrldrasterls1","5f70bc1fab8a57d286aa98b9bf375b3d8971e1e1", "3eda2676ef9d1e0bf1a8e2c6db980bbb01b5a6cf","3f06bafe093fe2292f0e1704ef755b96dd24883a", "1635195521"]
    # df.loc[len(df.index)] = ["jedicavebros0001@gmail.com", "secrldrasterls1", "a6ec91cb7cf1ba167af25945671c3ecfd1422b69","7c17702e1cccd6786b139c963a7bd9ffac9ca80f", "fde88c316f792aba6b73cb6dcb98836840e94b09", "1635195910"]
    print(df)
    df.to_csv('loginInformation.csv', index=False)
    return



# call this everytime before making an api call to verify that the auth token has not expired
def refreshAccessToken():
    df = pd.read_csv('loginInformation.csv')
    user = df.loc[0]
    print(user["clientId"])
    params = {"client_id":user["clientId"], "client_secret":user["clientSecret"], "grant_type": "refresh_token", "refresh_token":user["refreshToken"]}
    r = requests.post('https://www.strava.com/api/v3/oauth/token',params=params)
    responseJson = json.loads(r.content)
    accessToken = responseJson["access_token"]
    expireAt = responseJson["expires_at"]
    refreshToken = responseJson["refresh_token"]
    df.loc[0, "accessToken"]= accessToken
    df.loc[0, "expireAt"]= expireAt
    df.loc[0, "refreshToken"] = refreshToken
    df.to_csv('loginInformation.csv', index=False)


def main():
    refreshAccessToken()

if __name__ == '__main__':
    main()