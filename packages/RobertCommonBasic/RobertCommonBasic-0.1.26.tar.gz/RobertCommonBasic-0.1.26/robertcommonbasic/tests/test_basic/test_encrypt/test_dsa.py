import base64
from robertcommonbasic.basic.encrypt.dsa import dsa_sign, dsa_verify, get_key, generate_dsa_key, generate_dsa_key1
from cryptography.hazmat.primitives import hashes

from rsa import core, PublicKey, transform





def test():
    dsa_512_private = [48, -127, -58, 2, 1, 0, 48, -127, -88, 6, 7, 42, -122, 72, -50, 56, 4, 1, 48, -127, -100, 2, 65,
                       0, -4, -90, -126, -50, -114, 18, -54, -70, 38, -17, -52, -9, 17, 14, 82, 109, -80, 120, -80, 94,
                       -34, -53, -51, 30, -76, -94, 8, -13, -82, 22, 23, -82, 1, -13, 91, -111, -92, 126, 109, -10, 52,
                       19, -59, -31, 46, -48, -119, -101, -51, 19, 42, -51, 80, -39, -111, 81, -67, -60, 62, -25, 55,
                       89, 46, 23, 2, 21, 0, -106, 46, -35, -52, 54, -100, -70, -114, -69, 38, 14, -26, -74, -95, 38,
                       -39, 52, 110, 56, -59, 2, 64, 103, -124, 113, -78, 122, -100, -12, 78, -23, 26, 73, -59, 20, 125,
                       -79, -87, -86, -14, 68, -16, 90, 67, 77, 100, -122, -109, 29, 45, 20, 39, 27, -98, 53, 3, 11,
                       113, -3, 115, -38, 23, -112, 105, -77, 46, 41, 53, 99, 14, 28, 32, 98, 53, 77, 13, -94, 10, 108,
                       65, 110, 80, -66, 121, 76, -92, 4, 22, 2, 20, 97, -45, 97, 89, 40, -122, 77, 47, -60, 13, 126,
                       -15, 91, 108, 110, -84, 68, 96, 62, -118]
    dsa_512_public = [48, -127, -15, 48, -127, -88, 6, 7, 42, -122, 72, -50, 56, 4, 1, 48, -127, -100, 2, 65, 0, -4,
                      -90, -126, -50, -114, 18, -54, -70, 38, -17, -52, -9, 17, 14, 82, 109, -80, 120, -80, 94, -34,
                      -53, -51, 30, -76, -94, 8, -13, -82, 22, 23, -82, 1, -13, 91, -111, -92, 126, 109, -10, 52, 19,
                      -59, -31, 46, -48, -119, -101, -51, 19, 42, -51, 80, -39, -111, 81, -67, -60, 62, -25, 55, 89, 46,
                      23, 2, 21, 0, -106, 46, -35, -52, 54, -100, -70, -114, -69, 38, 14, -26, -74, -95, 38, -39, 52,
                      110, 56, -59, 2, 64, 103, -124, 113, -78, 122, -100, -12, 78, -23, 26, 73, -59, 20, 125, -79, -87,
                      -86, -14, 68, -16, 90, 67, 77, 100, -122, -109, 29, 45, 20, 39, 27, -98, 53, 3, 11, 113, -3, 115,
                      -38, 23, -112, 105, -77, 46, 41, 53, 99, 14, 28, 32, 98, 53, 77, 13, -94, 10, 108, 65, 110, 80,
                      -66, 121, 76, -92, 3, 68, 0, 2, 65, 0, -67, -6, 69, 111, 55, 36, -68, -21, -93, 72, -59, 98, 34,
                      -1, -56, -64, -65, 85, -39, 35, -62, -122, -45, -98, 111, -11, 4, -58, -82, -13, -124, -45, 87,
                      -34, -8, 115, 30, -120, -36, 101, -119, -113, -41, -30, 118, -15, 67, 11, 91, 27, -21, -43, -128,
                      -48, 94, 63, 112, -34, -94, 20, -62, 4, -108, 92]
    dsa_512_public_b64 = 'MIHxMIGoBgcqhkjOOAQBMIGcAkEA/KaCzo4Syrom78z3EQ5SbbB4sF7ey80etKII864WF64B81uRpH5t9jQTxeEu0ImbzRMqzVDZkVG9xD7nN1kuFwIVAJYu3cw2nLqOuyYO5rahJtk0bjjFAkBnhHGyepz0TukaScUUfbGpqvJE8FpDTWSGkx0tFCcbnjUDC3H9c9oXkGmzLik1Yw4cIGI1TQ2iCmxBblC+eUykA0QAAkEAvfpFbzckvOujSMViIv/IwL9V2SPChtOeb/UExq7zhNNX3vhzHojcZYmP1+J28UMLWxvr1YDQXj9w3qIUwgSUXA=='

    dsa_2048_private = [48, -126, 2, 92, 2, 1, 0, 48, -126, 2, 53, 6, 7, 42, -122, 72, -50, 56, 4, 1, 48, -126, 2, 40,
                        2, -126, 1, 1, 0, -113, 121, 53, -39, -71, -86, -23, -65, -85, -19, -120, 122, -49, 73, 81, -74,
                        -13, 46, -59, -98, 59, -81, 55, 24, -24, -22, -60, -106, 31, 62, -3, 54, 6, -25, 67, 81, -87,
                        -60, 24, 51, 57, -72, 9, -25, -62, -82, 28, 83, -101, -89, 71, 91, -123, -48, 17, -83, -72, -76,
                        121, -121, 117, 73, -124, 105, 92, -84, 14, -113, 20, -77, 54, 8, 40, -94, 47, -6, 39, 17, 10,
                        61, 98, -87, -109, 69, 52, 9, -96, -2, 105, 108, 70, 88, -8, 75, -35, 32, -127, -100, 55, 9,
                        -96, 16, 87, -79, -107, -83, -51, 0, 35, 61, -70, 84, -124, -74, 41, 31, -99, 100, -114, -8,
                        -125, 68, -122, 119, -105, -100, -20, 4, -76, 52, -90, -84, 46, 117, -23, -104, 93, -30, 61,
                        -80, 41, 47, -63, 17, -116, -97, -6, -99, -127, -127, -25, 51, -115, -73, -110, -73, 48, -41,
                        -71, -29, 73, 89, 47, 104, 9, -104, 114, 21, 57, 21, -22, 61, 107, -117, 70, 83, -58, 51, 69,
                        -113, -128, 59, 50, -92, -62, -32, -14, 114, -112, 37, 110, 78, 63, -118, 59, 8, 56, -95, -60,
                        80, -28, -31, -116, 26, 41, -93, 125, -33, 94, -95, 67, -34, 75, 102, -1, 4, -112, 62, -43, -49,
                        22, 35, -31, 88, -44, -121, -58, 8, -23, 127, 33, 28, -40, 29, -54, 35, -53, 110, 56, 7, 101,
                        -8, 34, -29, 66, -66, 72, 76, 5, 118, 57, 57, 96, 28, -42, 103, 2, 29, 0, -70, -10, -106, -90,
                        -123, 120, -9, -33, -34, -25, -6, 103, -55, 119, -57, -123, -17, 50, -78, 51, -70, -27, -128,
                        -64, -68, -43, 105, 93, 2, -126, 1, 0, 22, -90, 92, 88, 32, 72, 80, 112, 78, 117, 2, -93, -105,
                        87, 4, 13, 52, -38, 58, 52, 120, -63, 84, -44, -28, -91, -64, 45, 36, 46, -32, 79, -106, -26,
                        30, 75, -48, -112, 74, -67, -84, -113, 55, -18, -79, -32, -97, 49, -126, -46, 60, -112, 67, -53,
                        100, 47, -120, 0, 65, 96, -19, -7, -54, 9, -77, 32, 118, -89, -100, 50, -90, 39, -14, 71, 62,
                        -111, -121, -101, -94, -60, -25, 68, -67, 32, -127, 84, 76, -75, 91, -128, 44, 54, -115, 31,
                        -88, 62, -44, -119, -23, 78, 15, -96, 104, -114, 50, 66, -118, 92, 120, -60, 120, -58, -115, 5,
                        39, -73, 28, -102, 58, -69, 11, 11, -31, 44, 68, 104, -106, 57, -25, -45, -50, 116, -37, 16, 26,
                        101, -86, 43, -121, -10, 76, 104, 38, -37, 62, -57, 47, 75, 85, -103, -125, 75, -76, -19, -80,
                        47, 124, -112, -23, -92, -106, -45, -91, 93, 83, 91, -21, -4, 69, -44, -10, 25, -10, 63, 61,
                        -19, -69, -121, 57, 37, -62, -14, 36, -32, 119, 49, 41, 109, -88, -121, -20, 30, 71, 72, -8,
                        126, -5, 95, -34, -73, 84, -124, 49, 107, 34, 50, -34, -27, 83, -35, -81, 2, 17, 43, 13, 31, 2,
                        -38, 48, -105, 50, 36, -2, 39, -82, -38, -117, -99, 75, 41, 34, -39, -70, -117, -29, -98, -39,
                        -31, 3, -90, 60, 82, -127, 11, -58, -120, -73, -30, -19, 67, 22, -31, -17, 23, -37, -34, 4, 30,
                        2, 28, 119, -15, -4, 97, 110, 24, 75, 77, -69, 84, 118, 64, -13, -39, 111, 22, -12, 77, -108,
                        75, -53, 39, 31, -90, -51, -86, -28, 17]
    dsa_2048_public = [48, -126, 3, 66, 48, -126, 2, 53, 6, 7, 42, -122, 72, -50, 56, 4, 1, 48, -126, 2, 40, 2, -126, 1,
                       1, 0, -113, 121, 53, -39, -71, -86, -23, -65, -85, -19, -120, 122, -49, 73, 81, -74, -13, 46,
                       -59, -98, 59, -81, 55, 24, -24, -22, -60, -106, 31, 62, -3, 54, 6, -25, 67, 81, -87, -60, 24, 51,
                       57, -72, 9, -25, -62, -82, 28, 83, -101, -89, 71, 91, -123, -48, 17, -83, -72, -76, 121, -121,
                       117, 73, -124, 105, 92, -84, 14, -113, 20, -77, 54, 8, 40, -94, 47, -6, 39, 17, 10, 61, 98, -87,
                       -109, 69, 52, 9, -96, -2, 105, 108, 70, 88, -8, 75, -35, 32, -127, -100, 55, 9, -96, 16, 87, -79,
                       -107, -83, -51, 0, 35, 61, -70, 84, -124, -74, 41, 31, -99, 100, -114, -8, -125, 68, -122, 119,
                       -105, -100, -20, 4, -76, 52, -90, -84, 46, 117, -23, -104, 93, -30, 61, -80, 41, 47, -63, 17,
                       -116, -97, -6, -99, -127, -127, -25, 51, -115, -73, -110, -73, 48, -41, -71, -29, 73, 89, 47,
                       104, 9, -104, 114, 21, 57, 21, -22, 61, 107, -117, 70, 83, -58, 51, 69, -113, -128, 59, 50, -92,
                       -62, -32, -14, 114, -112, 37, 110, 78, 63, -118, 59, 8, 56, -95, -60, 80, -28, -31, -116, 26, 41,
                       -93, 125, -33, 94, -95, 67, -34, 75, 102, -1, 4, -112, 62, -43, -49, 22, 35, -31, 88, -44, -121,
                       -58, 8, -23, 127, 33, 28, -40, 29, -54, 35, -53, 110, 56, 7, 101, -8, 34, -29, 66, -66, 72, 76,
                       5, 118, 57, 57, 96, 28, -42, 103, 2, 29, 0, -70, -10, -106, -90, -123, 120, -9, -33, -34, -25,
                       -6, 103, -55, 119, -57, -123, -17, 50, -78, 51, -70, -27, -128, -64, -68, -43, 105, 93, 2, -126,
                       1, 0, 22, -90, 92, 88, 32, 72, 80, 112, 78, 117, 2, -93, -105, 87, 4, 13, 52, -38, 58, 52, 120,
                       -63, 84, -44, -28, -91, -64, 45, 36, 46, -32, 79, -106, -26, 30, 75, -48, -112, 74, -67, -84,
                       -113, 55, -18, -79, -32, -97, 49, -126, -46, 60, -112, 67, -53, 100, 47, -120, 0, 65, 96, -19,
                       -7, -54, 9, -77, 32, 118, -89, -100, 50, -90, 39, -14, 71, 62, -111, -121, -101, -94, -60, -25,
                       68, -67, 32, -127, 84, 76, -75, 91, -128, 44, 54, -115, 31, -88, 62, -44, -119, -23, 78, 15, -96,
                       104, -114, 50, 66, -118, 92, 120, -60, 120, -58, -115, 5, 39, -73, 28, -102, 58, -69, 11, 11,
                       -31, 44, 68, 104, -106, 57, -25, -45, -50, 116, -37, 16, 26, 101, -86, 43, -121, -10, 76, 104,
                       38, -37, 62, -57, 47, 75, 85, -103, -125, 75, -76, -19, -80, 47, 124, -112, -23, -92, -106, -45,
                       -91, 93, 83, 91, -21, -4, 69, -44, -10, 25, -10, 63, 61, -19, -69, -121, 57, 37, -62, -14, 36,
                       -32, 119, 49, 41, 109, -88, -121, -20, 30, 71, 72, -8, 126, -5, 95, -34, -73, 84, -124, 49, 107,
                       34, 50, -34, -27, 83, -35, -81, 2, 17, 43, 13, 31, 2, -38, 48, -105, 50, 36, -2, 39, -82, -38,
                       -117, -99, 75, 41, 34, -39, -70, -117, -29, -98, -39, -31, 3, -90, 60, 82, -127, 11, -58, -120,
                       -73, -30, -19, 67, 22, -31, -17, 23, -37, -34, 3, -126, 1, 5, 0, 2, -126, 1, 0, 103, 117, 22, 46,
                       9, 70, 35, 56, 83, -24, -94, -109, -5, -64, -16, -125, -112, -33, 126, 15, -100, 10, -105, -21,
                       -49, 84, 65, 4, 103, -44, -115, 119, 74, 20, -17, 8, 75, -105, -116, -21, 85, -34, -57, 38, 64,
                       113, -58, 24, -63, -30, -94, -100, 40, -102, 37, 43, 60, -72, 71, -60, -59, 7, -32, -111, 83,
                       -24, 86, 72, -1, 70, 122, 9, -123, 58, -100, 9, -53, -109, -90, 86, -74, 100, -59, -2, -59, -95,
                       -119, -12, -46, 57, 38, 36, 52, -85, -5, -40, 63, -58, 73, -76, 97, 22, -124, 35, 60, -87, 50,
                       -63, 86, 7, 17, -86, 83, -17, -117, 0, -53, -90, -81, -114, -20, -95, -83, -67, 89, 108, -68, 66,
                       -43, -32, -86, 59, -98, -72, 33, 106, 89, -115, 109, -27, 111, 119, 7, 68, -57, 50, 1, -97, 81,
                       -19, -88, -42, -27, 115, 43, -123, 57, -6, -99, -16, -94, -7, -93, 24, 7, -75, -100, 27, 92, 22,
                       43, -81, 49, -48, 43, -106, -13, -83, -94, 101, 127, 75, -54, -21, 74, -69, 114, -120, 21, 46,
                       104, -78, 40, -59, 88, -107, -85, 107, 96, -46, -101, 109, -32, -37, 113, 22, -65, -71, -81, 122,
                       11, 88, -37, -87, -48, 78, -1, -13, -89, -45, -77, -75, 63, 26, -71, 114, 71, 80, 2, 27, 8, -40,
                       101, -118, -13, 71, -106, 123, 116, 85, -109, -109, -122, -83, 115, -58, 81, 81, 75, -80, 117,
                       -5, -114, 92, 49, 17]
    dsa_2048_public_b64 = 'MIIDQjCCAjUGByqGSM44BAEwggIoAoIBAQCPeTXZuarpv6vtiHrPSVG28y7FnjuvNxjo6sSWHz79NgbnQ1GpxBgzObgJ58KuHFObp0dbhdARrbi0eYd1SYRpXKwOjxSzNggooi/6JxEKPWKpk0U0CaD+aWxGWPhL3SCBnDcJoBBXsZWtzQAjPbpUhLYpH51kjviDRIZ3l5zsBLQ0pqwudemYXeI9sCkvwRGMn/qdgYHnM423krcw17njSVkvaAmYchU5Feo9a4tGU8YzRY+AOzKkwuDycpAlbk4/ijsIOKHEUOThjBopo33fXqFD3ktm/wSQPtXPFiPhWNSHxgjpfyEc2B3KI8tuOAdl+CLjQr5ITAV2OTlgHNZnAh0AuvaWpoV499/e5/pnyXfHhe8ysjO65YDAvNVpXQKCAQAWplxYIEhQcE51AqOXVwQNNNo6NHjBVNTkpcAtJC7gT5bmHkvQkEq9rI837rHgnzGC0jyQQ8tkL4gAQWDt+coJsyB2p5wypifyRz6Rh5uixOdEvSCBVEy1W4AsNo0fqD7UielOD6BojjJCilx4xHjGjQUntxyaOrsLC+EsRGiWOefTznTbEBplqiuH9kxoJts+xy9LVZmDS7TtsC98kOmkltOlXVNb6/xF1PYZ9j897buHOSXC8iTgdzEpbaiH7B5HSPh++1/et1SEMWsiMt7lU92vAhErDR8C2jCXMiT+J67ai51LKSLZuovjntnhA6Y8UoELxoi34u1DFuHvF9veA4IBBQACggEAZ3UWLglGIzhT6KKT+8Dwg5Dffg+cCpfrz1RBBGfUjXdKFO8IS5eM61XexyZAccYYweKinCiaJSs8uEfExQfgkVPoVkj/RnoJhTqcCcuTpla2ZMX+xaGJ9NI5JiQ0q/vYP8ZJtGEWhCM8qTLBVgcRqlPviwDLpq+O7KGtvVlsvELV4Ko7nrghalmNbeVvdwdExzIBn1HtqNblcyuFOfqd8KL5oxgHtZwbXBYrrzHQK5bzraJlf0vK60q7cogVLmiyKMVYlatrYNKbbeDbcRa/ua96C1jbqdBO//On07O1Pxq5ckdQAhsI2GWK80eWe3RVk5OGrXPGUVFLsHX7jlwxEQ=='

    msg = 'hello'
    signature = dsa_sign(f"""-----BEGIN PRIVATE KEY-----\n{get_key(dsa_2048_private)}\n-----END PRIVATE KEY-----""".encode(), msg.encode())
    print(dsa_verify(f"""-----BEGIN PUBLIC KEY-----\n{get_key(dsa_2048_public)}\n-----END PUBLIC KEY-----""".encode(), msg.encode(), signature))
    print()


def generate():
    server_private_pem, server_public_pem = generate_dsa_key(2048, format='DER')


    #server_private_pem1, server_public_pem1, client_private_pem1, client_public_pem1 = generate_dsa_key1(1024)
    #aa = base64.b64encode(server_private_pem)
    aa = []
    for a in server_private_pem:
        if a > 128:
            a = a - 256
        aa.append(a)
    print(aa)


def sign(dsa_512_private: list, input: str, algorithm: str = 'SHA256') -> str:
    signature = dsa_sign(f"""-----BEGIN PRIVATE KEY-----\n{get_key(dsa_512_private)}\n-----END PRIVATE KEY-----""".encode(), input.encode(), algorithm)
    return base64.b64encode(signature).decode()


def test1(dsa_512_private: list, dsa_512_public: list, input: str, algorithm: str = 'SHA256'):
    signature = dsa_sign(f"""-----BEGIN PRIVATE KEY-----\n{get_key(dsa_512_private)}\n-----END PRIVATE KEY-----""".encode(), input.encode(), algorithm)
    print(dsa_verify(f"""-----BEGIN PUBLIC KEY-----\n{get_key(dsa_512_public)}\n-----END PUBLIC KEY-----""".encode(), input.encode(), signature, algorithm))


def convert_to_list(datas: bytes):
    aa = []
    for i, a in enumerate(datas):
        if a >= 128:
            a = a - 256
        aa.append(a)
    return aa


def test_cao(hostId: str, point_limit: str):
    # a1 = [48, -126, 3, 66, 48, -126, 2, 53, 6, 7, 42, -122, 72, -50, 56, 4, 1, 48, -126, 2, 40, 2, -126, 1, 1, 0, -113, 121, 53, -39, -71, -86, -23, -65, -85, -19, -120, 122, -49, 73, 81, -74, -13, 46, -59, -98, 59, -81, 55, 24, -24, -22, -60, -106, 31, 62, -3, 54, 6, -25, 67, 81, -87, -60, 24, 51, 57, -72, 9, -25, -62, -82, 28, 83, -101, -89, 71, 91, -123, -48, 17, -83, -72, -76, 121, -121, 117, 73, -124, 105, 92, -84, 14, -113, 20, -77, 54, 8, 40, -94, 47, -6, 39, 17, 10, 61, 98, -87, -109, 69, 52, 9, -96, -2, 105, 108, 70, 88, -8, 75, -35, 32, -127, -100, 55, 9, -96, 16, 87, -79, -107, -83, -51, 0, 35, 61, -70, 84, -124, -74, 41, 31, -99, 100, -114, -8, -125, 68, -122, 119, -105, -100, -20, 4, -76, 52, -90, -84, 46, 117, -23, -104, 93, -30, 61, -80, 41, 47, -63, 17, -116, -97, -6, -99, -127, -127, -25, 51, -115, -73, -110, -73, 48, -41, -71, -29, 73, 89, 47, 104, 9, -104, 114, 21, 57, 21, -22, 61, 107, -117, 70, 83, -58, 51, 69, -113, -128, 59, 50, -92, -62, -32, -14, 114, -112, 37, 110, 78, 63, -118, 59, 8, 56, -95, -60, 80, -28, -31, -116, 26, 41, -93, 125, -33, 94, -95, 67, -34, 75, 102, -1, 4, -112, 62, -43, -49, 22, 35, -31, 88, -44, -121, -58, 8, -23, 127, 33, 28, -40, 29, -54, 35, -53, 110, 56, 7, 101, -8, 34, -29, 66, -66, 72, 76, 5, 118, 57, 57, 96, 28, -42, 103, 2, 29, 0, -70, -10, -106, -90, -123, 120, -9, -33, -34, -25, -6, 103, -55, 119, -57, -123, -17, 50, -78, 51, -70, -27, -128, -64, -68, -43, 105, 93, 2, -126, 1, 0, 22, -90, 92, 88, 32, 72, 80, 112, 78, 117, 2, -93, -105, 87, 4, 13, 52, -38, 58, 52, 120, -63, 84, -44, -28, -91, -64, 45, 36, 46, -32, 79, -106, -26, 30, 75, -48, -112, 74, -67, -84, -113, 55, -18, -79, -32, -97, 49, -126, -46, 60, -112, 67, -53, 100, 47, -120, 0, 65, 96, -19, -7, -54, 9, -77, 32, 118, -89, -100, 50, -90, 39, -14, 71, 62, -111, -121, -101, -94, -60, -25, 68, -67, 32, -127, 84, 76, -75, 91, -128, 44, 54, -115, 31, -88, 62, -44, -119, -23, 78, 15, -96, 104, -114, 50, 66, -118, 92, 120, -60, 120, -58, -115, 5, 39, -73, 28, -102, 58, -69, 11, 11, -31, 44, 68, 104, -106, 57, -25, -45, -50, 116, -37, 16, 26, 101, -86, 43, -121, -10, 76, 104, 38, -37, 62, -57, 47, 75, 85, -103, -125, 75, -76, -19, -80, 47, 124, -112, -23, -92, -106, -45, -91, 93, 83, 91, -21, -4, 69, -44, -10, 25, -10, 63, 61, -19, -69, -121, 57, 37, -62, -14, 36, -32, 119, 49, 41, 109, -88, -121, -20, 30, 71, 72, -8, 126, -5, 95, -34, -73, 84, -124, 49, 107, 34, 50, -34, -27, 83, -35, -81, 2, 17, 43, 13, 31, 2, -38, 48, -105, 50, 36, -2, 39, -82, -38, -117, -99, 75, 41, 34, -39, -70, -117, -29, -98, -39, -31, 3, -90, 60, 82, -127, 11, -58, -120, -73, -30, -19, 67, 22, -31, -17, 23, -37, -34, 3, -126, 1, 5, 0, 2, -126, 1, 0, 40, -77, -65, -72, 1, 14, 71, -20, 49, 72, -90, 105, 36, -90, -99, 74, -73, -119, 90, -87, 114, 47, 21, -30, 29, 2, 99, -32, 53, 69, 100, -125, -13, 55, 122, -82, 51, -2, -3, 16, 89, -107, -116, -38, -19, -98, 49, -14, 2, 63, 118, 43, -43, 31, -66, -107, -103, -33, 127, -61, -115, 16, 127, 47, 65, -10, -128, -90, -15, 28, -45, 17, -49, -121, 25, -113, 1, -29, 58, -45, 82, -62, -47, -44, -71, -2, 90, -32, -56, 115, -62, -40, -78, 23, -77, 44, -104, 112, 15, 91, -41, 106, -37, 50, 61, 109, -116, -117, 127, -88, -2, 45, -31, 114, 30, 108, -50, -26, 36, -10, -105, -120, 19, -59, 51, 125, 62, -39, 116, 113, -18, 104, 109, -45, 23, 77, 61, 85, -55, 4, 104, -1, -121, -84, -98, -111, 98, 30, -98, -57, -58, -40, 87, 24, 48, -96, 116, 68, 12, -66, 78, 34, -1, -42, 78, -3, 64, 60, -15, 103, 64, -20, 121, 62, -68, -125, -44, 33, 1, 23, 49, 82, 56, -52, -52, 80, 54, -6, 92, -117, -116, 44, -34, -23, -88, 71, -66, -6, -20, 122, -100, 47, 26, -114, 94, -128, 83, 44, -63, -36, -26, 55, -30, -96, 94, -80, -24, -12, 101, -20, 110, -14, -41, -58, 71, 59, -2, -39, 51, -93, -30, -105, 96, -28, -89, 62, 20, -54, 6, 95, -13, 14, -118, 82, -99, 123, 5, 54, 36, 123, -118, 85, 7, -102, 39, -120]
    server_private_pem, server_public_pem = generate_dsa_key(2048, format='DER')
    input = f'{hostId}~!@#$%^&*ifcCbusTcp~!@#$%^&*'
    signature = dsa_sign(server_private_pem, input.encode(), 'DER', 'SHA256')
    result = dsa_verify(server_public_pem, input.encode(), signature, 'DER', 'SHA256')
    with open('sign.log', 'w') as f:
        f.write('''逻辑
	启动
		setNiagaraVersion
		setVendorVersion
		setHostId
		setMode
		加载授权文件
			授权文件不存在
				创建授权文件
					添加<license>
					添加<feature>
						point.limit = none
						signature = none
					添加<signature>
						signature = none
				返回
			
			读取授权文件
				如果<feature>.signature == none
					启动demo
				否则
					signBytes = <feature>.signature base64解码
					limit = '' 或者具体数字枚举编号
					input = getHostId() + "~!@#$%^&*" + "ifcCbusTcp" + "~!@#$%^&*" + limit.getBytes()
					如果 verify(false, input, signBytes)
						SHA256withDSA 默认512长度	
					
						启动
					否则
						启动demo''')

        f.write('\n\n')
        f.write('DSA - SHA256 - 2048bit\n')
        f.write(f'[server_private_pem]: {len(server_private_pem)}\n')
        #f.write(f'{server_private_pem.decode()}\n')
        f.write(f'{base64.b64encode(server_private_pem).decode()}\n')
        f.write(f"{convert_to_list(server_private_pem)}\n")
        f.write(f'[server_public_pem]: {len(server_public_pem)}\n')
        #f.write(f'{server_public_pem.decode()}\n')
        f.write(f'{base64.b64encode(server_public_pem).decode()}\n')
        f.write(f"{convert_to_list(server_public_pem)}\n")
        f.write(f"[input]: {input}\n")
        f.write(f"[signature]: {base64.b64encode(signature).decode()}\n")
        f.write(f"[result]: {result}\n")


def test_cao1(hostId: str, point_limit: str):
    # a1 = [48, -126, 3, 66, 48, -126, 2, 53, 6, 7, 42, -122, 72, -50, 56, 4, 1, 48, -126, 2, 40, 2, -126, 1, 1, 0, -113, 121, 53, -39, -71, -86, -23, -65, -85, -19, -120, 122, -49, 73, 81, -74, -13, 46, -59, -98, 59, -81, 55, 24, -24, -22, -60, -106, 31, 62, -3, 54, 6, -25, 67, 81, -87, -60, 24, 51, 57, -72, 9, -25, -62, -82, 28, 83, -101, -89, 71, 91, -123, -48, 17, -83, -72, -76, 121, -121, 117, 73, -124, 105, 92, -84, 14, -113, 20, -77, 54, 8, 40, -94, 47, -6, 39, 17, 10, 61, 98, -87, -109, 69, 52, 9, -96, -2, 105, 108, 70, 88, -8, 75, -35, 32, -127, -100, 55, 9, -96, 16, 87, -79, -107, -83, -51, 0, 35, 61, -70, 84, -124, -74, 41, 31, -99, 100, -114, -8, -125, 68, -122, 119, -105, -100, -20, 4, -76, 52, -90, -84, 46, 117, -23, -104, 93, -30, 61, -80, 41, 47, -63, 17, -116, -97, -6, -99, -127, -127, -25, 51, -115, -73, -110, -73, 48, -41, -71, -29, 73, 89, 47, 104, 9, -104, 114, 21, 57, 21, -22, 61, 107, -117, 70, 83, -58, 51, 69, -113, -128, 59, 50, -92, -62, -32, -14, 114, -112, 37, 110, 78, 63, -118, 59, 8, 56, -95, -60, 80, -28, -31, -116, 26, 41, -93, 125, -33, 94, -95, 67, -34, 75, 102, -1, 4, -112, 62, -43, -49, 22, 35, -31, 88, -44, -121, -58, 8, -23, 127, 33, 28, -40, 29, -54, 35, -53, 110, 56, 7, 101, -8, 34, -29, 66, -66, 72, 76, 5, 118, 57, 57, 96, 28, -42, 103, 2, 29, 0, -70, -10, -106, -90, -123, 120, -9, -33, -34, -25, -6, 103, -55, 119, -57, -123, -17, 50, -78, 51, -70, -27, -128, -64, -68, -43, 105, 93, 2, -126, 1, 0, 22, -90, 92, 88, 32, 72, 80, 112, 78, 117, 2, -93, -105, 87, 4, 13, 52, -38, 58, 52, 120, -63, 84, -44, -28, -91, -64, 45, 36, 46, -32, 79, -106, -26, 30, 75, -48, -112, 74, -67, -84, -113, 55, -18, -79, -32, -97, 49, -126, -46, 60, -112, 67, -53, 100, 47, -120, 0, 65, 96, -19, -7, -54, 9, -77, 32, 118, -89, -100, 50, -90, 39, -14, 71, 62, -111, -121, -101, -94, -60, -25, 68, -67, 32, -127, 84, 76, -75, 91, -128, 44, 54, -115, 31, -88, 62, -44, -119, -23, 78, 15, -96, 104, -114, 50, 66, -118, 92, 120, -60, 120, -58, -115, 5, 39, -73, 28, -102, 58, -69, 11, 11, -31, 44, 68, 104, -106, 57, -25, -45, -50, 116, -37, 16, 26, 101, -86, 43, -121, -10, 76, 104, 38, -37, 62, -57, 47, 75, 85, -103, -125, 75, -76, -19, -80, 47, 124, -112, -23, -92, -106, -45, -91, 93, 83, 91, -21, -4, 69, -44, -10, 25, -10, 63, 61, -19, -69, -121, 57, 37, -62, -14, 36, -32, 119, 49, 41, 109, -88, -121, -20, 30, 71, 72, -8, 126, -5, 95, -34, -73, 84, -124, 49, 107, 34, 50, -34, -27, 83, -35, -81, 2, 17, 43, 13, 31, 2, -38, 48, -105, 50, 36, -2, 39, -82, -38, -117, -99, 75, 41, 34, -39, -70, -117, -29, -98, -39, -31, 3, -90, 60, 82, -127, 11, -58, -120, -73, -30, -19, 67, 22, -31, -17, 23, -37, -34, 3, -126, 1, 5, 0, 2, -126, 1, 0, 40, -77, -65, -72, 1, 14, 71, -20, 49, 72, -90, 105, 36, -90, -99, 74, -73, -119, 90, -87, 114, 47, 21, -30, 29, 2, 99, -32, 53, 69, 100, -125, -13, 55, 122, -82, 51, -2, -3, 16, 89, -107, -116, -38, -19, -98, 49, -14, 2, 63, 118, 43, -43, 31, -66, -107, -103, -33, 127, -61, -115, 16, 127, 47, 65, -10, -128, -90, -15, 28, -45, 17, -49, -121, 25, -113, 1, -29, 58, -45, 82, -62, -47, -44, -71, -2, 90, -32, -56, 115, -62, -40, -78, 23, -77, 44, -104, 112, 15, 91, -41, 106, -37, 50, 61, 109, -116, -117, 127, -88, -2, 45, -31, 114, 30, 108, -50, -26, 36, -10, -105, -120, 19, -59, 51, 125, 62, -39, 116, 113, -18, 104, 109, -45, 23, 77, 61, 85, -55, 4, 104, -1, -121, -84, -98, -111, 98, 30, -98, -57, -58, -40, 87, 24, 48, -96, 116, 68, 12, -66, 78, 34, -1, -42, 78, -3, 64, 60, -15, 103, 64, -20, 121, 62, -68, -125, -44, 33, 1, 23, 49, 82, 56, -52, -52, 80, 54, -6, 92, -117, -116, 44, -34, -23, -88, 71, -66, -6, -20, 122, -100, 47, 26, -114, 94, -128, 83, 44, -63, -36, -26, 55, -30, -96, 94, -80, -24, -12, 101, -20, 110, -14, -41, -58, 71, 59, -2, -39, 51, -93, -30, -105, 96, -28, -89, 62, 20, -54, 6, 95, -13, 14, -118, 82, -99, 123, 5, 54, 36, 123, -118, 85, 7, -102, 39, -120]

    server_public_pem = '''-----BEGIN PUBLIC KEY-----
MIHxMIGoBgcqhkjOOAQBMIGcAkEA1QkGZ0yhLSNYTTNAp/z8yX8rc/BbT1BOTm/g
0eJ+jHDQgFYhw9oxiC4ayKz4dFR5+qX1n6MJN+UPRiFANAgjHwIVAOgOnlMqbq/r
8gy24/p4U/IoNCuTAkB8pP2MZPGp7ASx8Cr9s4uNpYGunnLfgSNNCKVhc0/YSmTU
4TRf30oOv/vLUWGi32y7VW8nrU/e4Zc40ijwQvc+A0QAAkEAxArP1KYWL0vWAALV
4RTbs8ekJ4vO/EtepCRMZrlAXJ4eVDhZgQ0jDP0Wbo49gOUmodAtf7u3KPiaEle1
RckmYw==
-----END PUBLIC KEY-----'''

    server_private_pem = '''-----BEGIN PRIVATE KEY-----
MIHGAgEAMIGoBgcqhkjOOAQBMIGcAkEA1QkGZ0yhLSNYTTNAp/z8yX8rc/BbT1BO
Tm/g0eJ+jHDQgFYhw9oxiC4ayKz4dFR5+qX1n6MJN+UPRiFANAgjHwIVAOgOnlMq
bq/r8gy24/p4U/IoNCuTAkB8pP2MZPGp7ASx8Cr9s4uNpYGunnLfgSNNCKVhc0/Y
SmTU4TRf30oOv/vLUWGi32y7VW8nrU/e4Zc40ijwQvc+BBYCFHmJeT9diEmjhN69
L2ZNg1wito0F
-----END PRIVATE KEY-----'''

    dsa_512_public = [48, -127, -15, 48, -127, -88, 6, 7, 42, -122, 72, -50, 56, 4, 1, 48, -127, -100, 2, 65, 0, -4,
                      -90, -126, -50, -114, 18, -54, -70, 38, -17, -52, -9, 17, 14, 82, 109, -80, 120, -80, 94, -34,
                      -53, -51, 30, -76, -94, 8, -13, -82, 22, 23, -82, 1, -13, 91, -111, -92, 126, 109, -10, 52, 19,
                      -59, -31, 46, -48, -119, -101, -51, 19, 42, -51, 80, -39, -111, 81, -67, -60, 62, -25, 55, 89, 46,
                      23, 2, 21, 0, -106, 46, -35, -52, 54, -100, -70, -114, -69, 38, 14, -26, -74, -95, 38, -39, 52,
                      110, 56, -59, 2, 64, 103, -124, 113, -78, 122, -100, -12, 78, -23, 26, 73, -59, 20, 125, -79, -87,
                      -86, -14, 68, -16, 90, 67, 77, 100, -122, -109, 29, 45, 20, 39, 27, -98, 53, 3, 11, 113, -3, 115,
                      -38, 23, -112, 105, -77, 46, 41, 53, 99, 14, 28, 32, 98, 53, 77, 13, -94, 10, 108, 65, 110, 80,
                      -66, 121, 76, -92, 3, 68, 0, 2, 65, 0, -67, -6, 69, 111, 55, 36, -68, -21, -93, 72, -59, 98, 34,
                      -1, -56, -64, -65, 85, -39, 35, -62, -122, -45, -98, 111, -11, 4, -58, -82, -13, -124, -45, 87,
                      -34, -8, 115, 30, -120, -36, 101, -119, -113, -41, -30, 118, -15, 67, 11, 91, 27, -21, -43, -128,
                      -48, 94, 63, 112, -34, -94, 20, -62, 4, -108, 92]

    aa = get_key(dsa_512_public)
    ab = convert_to_list(base64.b64decode(aa.encode()))
    for i in range(len(ab)):
        if dsa_512_public[i] != ab[i]:
            print(i)
    print(aa)

    input = f'{hostId}~!@#$%^&*ifcCbusTcp~!@#$%^&*'
    signature = dsa_sign(server_private_pem.encode(), input.encode(), 'PEM', 'SHA256')
    result = dsa_verify(server_public_pem.encode(), input.encode(), signature, 'PEM', 'SHA256')
    with open('sign.log', 'w') as f:
        f.write('''逻辑
	启动
		setNiagaraVersion
		setVendorVersion
		setHostId
		setMode
		加载授权文件
			授权文件不存在
				创建授权文件
					添加<license>
					添加<feature>
						point.limit = none
						signature = none
					添加<signature>
						signature = none
				返回

			读取授权文件
				如果<feature>.signature == none
					启动demo
				否则
					signBytes = <feature>.signature base64解码
					limit = '' 或者具体数字枚举编号
					input = getHostId() + "~!@#$%^&*" + "ifcCbusTcp" + "~!@#$%^&*" + limit.getBytes()
					如果 verify(false, input, signBytes)
						SHA256withDSA 默认512长度	

						启动
					否则
						启动demo''')

        f.write('\n\n')
        f.write('DSA - SHA256 - 512bit\n')
        f.write(f'{server_private_pem}\n')
        f.write(f'{server_public_pem}\n')

        _server_private_pem = server_private_pem.replace('-----BEGIN PRIVATE KEY-----\n', '').replace('\n-----END PRIVATE KEY-----', '')
        f.write(f'[server_private_pem]: {len(_server_private_pem.encode())}\n')
        f.write(f"{convert_to_list(base64.b64decode(_server_private_pem.encode()))}\n")

        _server_public_pem = server_public_pem.replace('-----BEGIN PUBLIC KEY-----\n', '').replace('\n-----END PUBLIC KEY-----', '')
        f.write(f'[server_public_pem]: {len(_server_public_pem.encode())}\n')
        f.write(f"{convert_to_list(base64.b64decode(_server_public_pem.encode()))}\n")

        f.write(f"[input]: {input}\n")
        f.write(f"[signature]: {base64.b64encode(signature).decode()}\n")
        f.write(f"[result]: {result}\n")


def test_cao2(hostId: str, point_limit: str):

    server_public_pem = '''-----BEGIN PUBLIC KEY-----
MIHwMIGoBgcqhkjOOAQBMIGcAkEAkSkklSGOMlDgH4epSsfm4LslBH4Sze+xleHn
svaqZTI03YSUFPSdWcdehDt5OvHxyBZxn9Yb6J3PsVEdzoDi6wIVAOSDQXeC6DoD
vVw7BpEYEir2RGKzAkBpgMEBLNxT0wpxCfmWD1N4U4ZgHNUzl/bcuR3dTIaQBeNY
JxeLdBNmaWg2fGfi9yp7mVKI/zdSPt0ZV9E9XMsXA0MAAkBKcAMvihKPXFGp3Hry
8EMfGn5otkWo/Ilr940EuddrPYJfshWbcXb6XB03TmRW1rMFXJ6caJVrx0+bpbqf
HhFc
-----END PUBLIC KEY-----'''

    server_private_pem = '''-----BEGIN PRIVATE KEY-----
MIHGAgEAMIGoBgcqhkjOOAQBMIGcAkEAkSkklSGOMlDgH4epSsfm4LslBH4Sze+x
leHnsvaqZTI03YSUFPSdWcdehDt5OvHxyBZxn9Yb6J3PsVEdzoDi6wIVAOSDQXeC
6DoDvVw7BpEYEir2RGKzAkBpgMEBLNxT0wpxCfmWD1N4U4ZgHNUzl/bcuR3dTIaQ
BeNYJxeLdBNmaWg2fGfi9yp7mVKI/zdSPt0ZV9E9XMsXBBYCFGSBiQhECCro7zfY
sR3gwZ1QIDPe
-----END PRIVATE KEY-----'''

    input = f'{hostId}~!@#$%^&*ifcCbusTcp~!@#$%^&*'
    signature = dsa_sign(server_private_pem.encode(), input.encode(), 'PEM', 'SHA256')
    result = dsa_verify(server_public_pem.encode(), input.encode(), signature, 'PEM', 'SHA256')
    with open('sign.log', 'w') as f:
        f.write('''逻辑
	启动
		setNiagaraVersion
		setVendorVersion
		setHostId
		setMode
		加载授权文件
			授权文件不存在
				创建授权文件
					添加<license>
					添加<feature>
						point.limit = none
						signature = none
					添加<signature>
						signature = none
				返回

			读取授权文件
				如果<feature>.signature == none
					启动demo
				否则
					signBytes = <feature>.signature base64解码
					limit = '' 或者具体数字枚举编号
					input = getHostId() + "~!@#$%^&*" + "ifcCbusTcp" + "~!@#$%^&*" + limit.getBytes()
					如果 verify(false, input, signBytes)
						SHA256withDSA 默认512长度	

						启动
					否则
						启动demo''')

        f.write('\n\n')
        f.write('DSA - SHA256 - 512bit\n')
        f.write(f'{server_private_pem}\n')
        f.write(f'{server_public_pem}\n')

        _server_private_pem = '''MIHGAgEAMIGoBgcqhkjOOAQBMIGcAkEAkSkklSGOMlDgH4epSsfm4LslBH4Sze+x
leHnsvaqZTI03YSUFPSdWcdehDt5OvHxyBZxn9Yb6J3PsVEdzoDi6wIVAOSDQXeC
6DoDvVw7BpEYEir2RGKzAkBpgMEBLNxT0wpxCfmWD1N4U4ZgHNUzl/bcuR3dTIaQ
BeNYJxeLdBNmaWg2fGfi9yp7mVKI/zdSPt0ZV9E9XMsXBBYCFGSBiQhECCro7zfY
sR3gwZ1QIDPe'''
        f.write(f'[server_private_pem]: {len(_server_private_pem.encode())}\n')
        f.write(f"{convert_to_list(base64.b64decode(_server_private_pem.encode()))}\n")

        _server_public_pem = '''MIHwMIGoBgcqhkjOOAQBMIGcAkEAkSkklSGOMlDgH4epSsfm4LslBH4Sze+xleHn
svaqZTI03YSUFPSdWcdehDt5OvHxyBZxn9Yb6J3PsVEdzoDi6wIVAOSDQXeC6DoD
vVw7BpEYEir2RGKzAkBpgMEBLNxT0wpxCfmWD1N4U4ZgHNUzl/bcuR3dTIaQBeNY
JxeLdBNmaWg2fGfi9yp7mVKI/zdSPt0ZV9E9XMsXA0MAAkBKcAMvihKPXFGp3Hry
8EMfGn5otkWo/Ilr940EuddrPYJfshWbcXb6XB03TmRW1rMFXJ6caJVrx0+bpbqf
HhFc'''
        f.write(f'[server_public_pem]: {len(_server_public_pem.encode())}\n')
        f.write(f"{convert_to_list(base64.b64decode(_server_public_pem.encode()))}\n")

        f.write(f"[input]: {input}\n")
        f.write(f"[signature]: {base64.b64encode(signature).decode()}\n")
        f.write(f"[result]: {result}\n")


def test_cao3(hostId: str, point_limit: str):

    server_public_pem = '''MIHwMIGoBgcqhkjOOAQBMIGcAkEAkSkklSGOMlDgH4epSsfm4LslBH4Sze+xleHn
svaqZTI03YSUFPSdWcdehDt5OvHxyBZxn9Yb6J3PsVEdzoDi6wIVAOSDQXeC6DoD
vVw7BpEYEir2RGKzAkBpgMEBLNxT0wpxCfmWD1N4U4ZgHNUzl/bcuR3dTIaQBeNY
JxeLdBNmaWg2fGfi9yp7mVKI/zdSPt0ZV9E9XMsXA0MAAkBKcAMvihKPXFGp3Hry
8EMfGn5otkWo/Ilr940EuddrPYJfshWbcXb6XB03TmRW1rMFXJ6caJVrx0+bpbqf
HhFc'''

    server_private_pem = '''MIHGAgEAMIGoBgcqhkjOOAQBMIGcAkEAkSkklSGOMlDgH4epSsfm4LslBH4Sze+x
leHnsvaqZTI03YSUFPSdWcdehDt5OvHxyBZxn9Yb6J3PsVEdzoDi6wIVAOSDQXeC
6DoDvVw7BpEYEir2RGKzAkBpgMEBLNxT0wpxCfmWD1N4U4ZgHNUzl/bcuR3dTIaQ
BeNYJxeLdBNmaWg2fGfi9yp7mVKI/zdSPt0ZV9E9XMsXBBYCFGSBiQhECCro7zfY
sR3gwZ1QIDPe'''

    aa = int.from_bytes(server_public_pem.encode(), "big", signed=False)
    a1 = convert_to_list(base64.b64decode(server_public_pem.encode()))
    b1 = get_key(a1)
    for i in range(len(b1)):
        if b1[i] != server_public_pem[i]:
            print(i)
    if b1 == server_public_pem:
        print(True)
    print()

test_cao3('Win-061E-5DE7-8EA0-E225', '')


