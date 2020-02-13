# BarterDude
[![Build Status](https://travis-ci.com/olxbr/BarterDude.svg?branch=master)](https://travis-ci.com/olxbr/BarterDude)
[![Coverage Status](https://coveralls.io/repos/github/olxbr/BarterDude/badge.svg?branch=master)](https://coveralls.io/github/olxbr/BarterDude?branch=master)

Message exchange engine to build pipelines using brokers like RabbitMQ. This project is build on top of [async-worker](https://github.com/b2wdigital/async-worker).

![barter](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMTEhUSERMVFhUXFhgaFhMYGBcXFhgVIBcbFxkbIBgYHSggGR4lHRkVITEhJy0rLy4uGR8zODMtNygtLisBCgoKDg0OGhAQGzclHiMvMi0vLy0vLS0wLy0tLy0vLy0uKy0uKy0tLSsvKzUtLS0tLS0tLS0rLS8tNTAtLS01Lf/AABEIAOEA4QMBIgACEQEDEQH/xAAbAAEAAgMBAQAAAAAAAAAAAAAABQYDBAcCAf/EAEUQAAICAQIDBQUEBwUGBwEAAAECAAMRBCEFEjEGE0FRYSIycYGRQlKhsRQjM1NigsEHFXLR8CQ0c6KywkNUY5Kjs+EW/8QAGgEBAAMBAQEAAAAAAAAAAAAAAAMEBQIBBv/EAC4RAAIBAgQDCAEFAQAAAAAAAAABAgMRBBIhMUFR8AUTIjJhcZHRgRShweHxsf/aAAwDAQACEQMRAD8A7jERAERBgCJzvinbi57bBpDWtFR5WudS3O3T2QPDO3r8Js8F7aWf+N3dw/8ARBW0Dz7p/fH+E59JB+op5st9SLvoXy3L3E1uH66u5BZUwZT4+viCDuCPIzZk5KIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAJWP7SuJPp+HXvWeViFrD/d52FfMPUc20s8iu1XBxq9Jdpm+2vsnycEMh+TBTPGGcg1dYqqooT3VQMfVjt+AH5zTU4II2I3BHUGb1gL0jmGLKCa7U8QAdj8Acj5zQny1dSU9TDqJqWpaez3H3R+8Gefrag6XJ4tj94PPxnUdDrEurW2tgyMMgicIqsKsGU4IIIPrLx2M40KrlrJ/U6okoM7Vage+mANg3X6ec1MBi3LwTLuFr38Mjo0RE1i+IiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAc//ALQOBvWx4hpl5iq41FP7yvzx5gSka2tPYtqOarUD1n0PUH1B2ndmXIweh8Jx3iHCxpdRZw6wctVrNborj0Vzu9ZPlnbHhkGZ+OwynHMtypiaOZZluQbNmSHCQziytTggd7X594m+3xXP0E0noYMUYcpU4YHwI6z3RcanV195TkD/AD+MxINxlmZmxdnc7L2b4qNTp0tHUjDDyYdZKTm3YXiy1ahkAxVqWyu+RXeBuh9GG4PpOkz6ajUzwUjapzzRTERElOxERAEREAREQBE+EwDAPsREAREQBERAEREAREQBERAERMOs1KVI1lhCooJZj4AQCA7ZdqRpFWusc+ot2qr/AO4+Sicz1VgDc2o5tRfnLOztyq3kijYY9Jt2a5y1+vYZe5ylJIx3dXhgeePxJkJMTHYtt5Ymbia7bsiT4s4s5bQrKxwHB8T4Pn1kZJHTswqy5/VklQNiT4nBOwE1Ate+7jyHKD8MnP8ASUKizO/MqS11M/C2yxrzjnxyk/ZsB5kP1GPnOx9n+JDUaeu7GCw9pfuuDysPkwM4411ZVVRWQg5Lkhsnw6AES5djuKmm0CzarVEkNjATVAAMM9OV1AYes0uzquV5LlzCTs8p0KJ8BkZxztDpdIvPqbkrHgCfaPoFG5+U2DRJSJzq/wDtMstPLw7h9146C2w9xXk9DuCxHxxNU8R7QWkH/Y6AeqhWdl9TzHf5TpRb2R45Jbs6fE5dVwnjLMTbxYKPDu6V/I4xPaaLjdZ9jidVg8raAP8ApM67qfL/AIcd9T5nTpR+P8c1dt76fSL3aV/tL2xufIZyF+YmhwvinGHsOn1J0qry5bUVBu8Rc7YUnl5m3x5dfDEmLuH1tX3RX2PEZO565J6sSevnK1aeTw8S1Rp5/FwKLxHUZP65nu8CRczD6AgTPoWCgGqyys+Qsb8iSJbW0ARcaeulT94rsP5V94/MTUu7Oiw5tusbxAHIij4KBKMot6qTXyW1G2ljX0HaPV1YzYLlz0sAVsejLt9RLfwXtHVqPZ3Sz923X5Ho3ylUs7PMPcuPwdAR9VwZGXUlWKt1U+H5gzyOIq0/PqjmWHjLbRnV4kL2T4kbqBznNiHlcnx+6fmuPnmTU04yUkmii1Z2YiInp4IiIAiIgCIiAJzvt5xQ26kaPJWqtRZeR47ZA+Q/EidA1FyorO5AVQSSfADrOSs41Oo1eoQkLfWVpVtmZlCnYfBSfoJWxU3GFluyGvK0dN2RGq1psZhgKhwFXwUDoP8AXnNOJsGnmTnByQcMPEDGQ3w8Mz5ttz9zH1ZsKQ1AUAkoWLY8AcYOPHpNUlQmBuxIycY5QM7eucj6TzVcykMhII6ETZAFvMxwhAyzAfqyfDb7JPpn4Tu+bbc93NSp8HM2NPxB0U15DVk5NbDmXPng9PlMV1PKAcqc/dOcfHymKcKUo7aHl2ieTiupGmtbSXNUUUc9Z/WBUO3NXzdCPLp0kl2c7J6UhNWzNqbLFDi648zEEZHXoPQSB4C3K5YjK8uHHmjHB+gyflLH2HJr/SNITkU2k1k/u33+gbOPiJ9D2VXz+Ge/DrrZluFabha5Z0QAYAAHkNp9iJuHAni+3lUnr5DzPgJ7msp5rTkHFQB8OVnYbf8AtH5zipPJFyJaNPvJqJ7ooFa43JJLMTuSx/y6SC1hpd+QHUtcRkKC6ZHmPAL6yd1N3KpPU4PKv3mxkD5zX4PWgrDqwd7AGss8Sfu/whegXwxMRycm5SPosqVoo+cI0HcpykkknJyS2PDGTuZjo4gwsNdq8uSeRugab14blPIQGxsSOYA/DIzNLT95aGr1Va5HR0zyMPArndT6eEjeup3tZEjK3x79t/ID+JlirXAAyTgYyep+Mq/GWzqGx4Iq/Pc/1kdXyM64okuwNx/Sr0z7JpqYj+Lndfy/KX2Uv+znTE/pGoI2d1rQ+a1ggn4c7OP5ZdJoYdNUopmbWd5sRESYjEREAREQBERAKZ/alqWGlWpdhdYEY/w4LEfPGJQeJX8tiomwpAVfiNyfmZ0zt9wVtTpv1ee8qbvEHmQCCPmCZzDUjvUF6jyW0fdfoDjwB/OZHaSne626v/Bn4xSv6HjVqD+sXofeH3W8fkfCYK7CpypIPp5T1RaV3GPIqdwR6ibentrw7CpRhDuxLjnyAuFO3n1zMtJSd72ZS3PGAV57FA8gNi++5/8A2Yb9SWHKByoOijp8T5n1n2quy58KGdz0A/y8BJjh3Z+tqRZfeKWd2SpSM5K7HPkM7TqMZ1NI/X7nqi5bEbw6tWWxWONgVJ8CDufXwmrfSyMVcYI8PTwPqPWZtVp309pRxhkO48CP6giebtYzLyZ9gH2VOCVHkGIyJzK2Wz3R49rPc8038qsB1IIz/r5y29nlzrbzk+zWgIHQnCjP4Sp6CrmtrXzdR8sy4di6cnUXnGXt5R5hRvj6t+E0+yE5Vl6fVv5JKfXX5LNERPqDs+O4UFmOAAST5ADJ/CaNWoCUCxmx3h58ucAc+6g+WByj5Rxy7lpbHVitY2zu7BOnluZi7UakVVAhSQLKwFHXAYdPPAB+ko416RjzNPs+PmmbGheo+0jrY2ffyCc+QHgPhMtOmRSSqgFuuNsnzk0KtPqkDcqWKRscAkePUbiad/BXXJpckfu7DkfJ/eHzyPhKcqD4MvwxEeKNUHcj/WJ6mjXqibTWyOjoBzAgYIbOMMNjgr4ek3pA1bcsxaaujHqLgilm6AZlD1usIyqnmvtbCJnJLsdtvAD+kunEtF3yhC5QZBYjrgeXkfWR2uoFFFjVKERVJWvlBax/slnOWLZwRg5nOTO1fY5m2ti58B4cNPp6qB9hQCfNurH5kkzfkF2K48ut0dWoAwxHLYnilq+y6n5/gRJ2adrGYIiIAiIgCIiAIiIAnLu0unGj4iPZC0atSCeq950YEfHlb6zqMr/bns/+m6R6hgWr7dL/AHbV3X5H3T6EyOrTzxscVIZo2OU62pUdkZCrKxBAOw+HpMVt2QFAwo3x5nzJmy9pvoFxGLa/1d6H3gRsCfh7vyE0J8zVThJoxppxdiwdjrDz3VrtZZSwrbxDDfA9TJX+7KrtFXUlubBYxVn9nluwC9RPhnqM9cSoaJXNiCrPecw5MdebwxLaxa+u5dawpFLKbVrqHO7HYWNjrjzlnDyzQytc16c9+BLSd42a63NDtZp259PX794qC2BPaPNnYbddp80vZYqHbVuaQiqxUDnflJxnA6AHrJqgd2tuk06qloqWxLl964e8c53G2NhPjXV95TqkrscanmF4zzIFxy2IV8N/akrowcs0v65e7s7X23JHTi3d9cPyVu7Rfo2qrBYOnMjq/TKE9fSWLsc+Dqqcfs9Qd/Rht+Uj+21dJfmR+V0wnc9RyAeyykeGJn4NqAuqSzw1dIyc7C6vZxj18/WWuzrU8S49daWOVG0pRRbIiJ9EeGlxVcirP/mKP/sEgu2dubKVz4O+PXZR+bSZ4+xWoOBnktpc/AWDP5zNr+Hh2DcldhUMvd2e6ynrg49lthgzNxsbyRsdnStTl7lA09zra3d2tUwAxynlz6kdGk3pu2GurKpz0252AYYcnp1U7/SZuKcB0jgBqbqj15GTv6wfQ7kD4GYeyvASrd7ZUtYUnu0AAJP3yB09Ad95S8cNpaGnno1I2cNee3XyWyvOMtux3Y+vjPUTDq9StaNY5wqjJP8ArxnOrY0ijV1nGaKs95aoIOOXIL58gg3J9MTRq73VOrOjVUochW9528CfIek9cG0xttOssQAsvLWNsivPQ+vj8fhJ2aOHwiVpSMnFY53cIfJBdnXGk4rZQNqtahurXwXUV+zYP5l5T/LOgzm3bnNaafVqBzabU1PnfPdse6sG3hhgT/hnSFbIyOhktaNpX5kdCWaB9iIkRKIiIAiIgCIiAIiIBzntzwZtLa3EKF5q3wNXVjYjp3n06/IyqXaetbaycmh+VgfHuydxnzG4nbr6VdSjAFWBBB6EHYicb1XCzS12gbOaSbdMfvUn3l+g+qeszMfQus66/wB+iliqWmZFk4jw0IO/q03J3FqFGryRZTsS3rt4yX1en5rja3ITgqy5BN2kbBJKjfKE/MCVbhPaCla6rLi5toDKiDo6EbAnpgSB4hxV7XFh9lggTK5BKgY3PwleWJpwjdcbadfH4IXVhFXXHrr2LH2h1ldWpXUVOBbWwVquqlANireRXwkLfx+z9alJNdVlhfkHUZGCM+Uiq0JIVQST0A3JkqnDK6sHVuVP7lN7D8fBZVdWpUbcdF1xIc8pPTQi6q2dgqgsx6AAkn5SR1tp09GLGQW1WrbWuQSh+2GPQZHh1zJTl1D1sNJUulq5SS5z3jgDO7e8fgMCSPZ/gVNKV3sotYorP3ihhggE8oOyEZ6yzhqEoSUk/wA/192LlDA1X4tvf6+7EppuOad0V+/pHMoODYgIyPInM2NBql1GRpbKrOU4dg4ZUPkQpzn/AFmWFNBSQCKq8EfcXp9J706VKxWsIDsWCgA+mcfOfR9++RKsNG+5D67s4bq3R7mUMpXCAAbjrvknB3kdwy5inJb+2qwlo/iA2f4OMMPjLiTKXr9KLNY1qlq3NCFWB95Q7D2lOxG8q125x14FzD+CVom/mAJGvRqc7XoB/wAJSc/XE8/3ba2RdqbGB+yvLUv/ACe1+Mo2XM0LvkZtVxJFbu1/WW/u135ds5duiD47+kg6XbXXb/7vU3vD3bLQd8Z6qDsPM5MdpNQlIq0NOK21B5SwBARDsTkdHfdQevU+EsfD9ClNa11qFVQBgegxL2EoZnmexn43EZFlW5sAY2ERE0zFIrtXpzZotSi45mpfGemeXP8ASWbszqe80mnsP2qkPz5RIXif7G3/AIb/APSZvdgc/wB3aTPXuU/KQV9l1yLmF2ZPxESsWhERAEREAREQBERAEpX9pfDW7uvXVftNKeZv4qD+0X5bN8jLrPNtYYFSMgggjzB2M8lFSVmeNXVmcO4ppeWwFBlbFD1gb+y2+B8DkTz+hqm97hP4B7Vn06L8/pJjinZziGl02pFbL3NAdqD1d068uwyuPj4ST7H8L0zUU6lV53dFbnffc9cA7DfMy6XZUqk23outl/hlzw+V3expcH0VroDp1WhGH7Y+1aw8cfd/CTnDuAVVHmwXfxd/aYn+ky6Bu7tehsDmJsq8MqffX4g7/OSMknQVKWXkbuDo0lBSitTxZWCpU9CCD8DtPgrCpyjoFwPgBiZJpcZ1qU1F7XVAfZBbYZMJN6F1tJXZL6niT11VV1rzaiwAIh6Dbd28lUbnz2A3M3eEcMWhOUEsxPNZYfedz1Y/5dB0ml2d0hOdTaMPYqhR4pSPdX4nqfU+km5omUaHHbOXT2N5Lv8A4cjm/DMhePXinUJY4xU9YrW37CNzZAY+AYYwem0s9tYYFWAIIIIO4IOxBEgv0O2lDTyDUafGFRiOdU+4ebZwOg9BOZRurHUZZXcwDfcTw16hgucsTgIN2J+A3nxeD6YD2eHsOnsjCjr6Nib5RdOmQtdCfwjmcnyGBufrIP0/Nll4nkiI4n2XW+q+qw/rbWFqkHeooMUjPowz65aYez3EzdUosBFy5S5MH2LF2YHwH9czYt13ObK6neqtOU3Wna13O+OZvdGMb+u2Jl0dSouK15FO/qSepYnck+Z3kyxHdaIgeG77zDS6xLCwRt1OGUgqwPqrYPzmeQ3HB3dlWrHVSK7f4qmOAT/hbB+cmZdo1VUjczsTQ7mduBH9odQK9Le7ZwtTk43PumT/AGV05r0enQ9VpQH48olS7ZlmpShPe1F9VI+BbmfPpyI+86AigAAdAMCc13siTDLwtnqIiVyyIiIAiIgCIiAIiIAiIgHi6oMrKwyGBBHoRgzlnYBzp7NVwywnm01pNWR107nK4+BP4idWnOf7S9G2lvp4vSpPdDutUo+1p2Ozfyk/Q+kkpyyyOKkc0Wia1ukWwDOzKco495W8x/l4yLs12urADaWvUHpz12CvI8yj9PkTJjT3q6K6HKsAQfMHeZJYqUoVPMinSxE6XlII6niFi+xVRps5ybGNrD+VcD8ZH6rgQyLdZab3QG1i37OtUGfZQY6tgdJbZprwMaxNRzOVDOtaMvlWPaBB6jvC+R48onCo06avYmWJq1WeOx3a6zUOKrkrya+8D1tkKAcYdfsGWDgvH9PqgTRYG5feG4YfEHeUvWcC1enDpVytbqmCNci8iVVqPLwJGcmRHCrRTw3U93+0tv7pChJY9BsRuR1M6dKEtY+hwqs4WUvXrrmdeic57O8Z1VdF71899dRUL33ssMAm3frgYli4F2yo1C5bNLezs+wPMMjDdDmQSpSVyeNaMrFjxKxxywrqRzjYp+qJxyg5PefzYx8pZwc7iaHGOGreoUnDKQyNjJVvPHiDuDIZq6sTwlaVyqW4Fyu5JR+qkbNaq5RvoCMeYEklzn2z7R6L5f5mYOM8FvCpaXDClw5qRfeGCrHJ3yASQB5TKlq8psG+R1G/s+GPzlSUXG1y7CSk3Y+6rTC1Hqbo6lT8x1+RwZo9nNSz0BX9+smt/wDEu2fn1m1VrkZgqnORkH7J9M+ciOK64aS2yzGe/UGtB1a8eyFHx2/GWcFPLLK+JXx9LPC64G1wyr9I4rzda9FV8v0m3+q1j198S9yE7IcG/RdOFc81rsbLn+9a27H4DZR6ASbk9SWaVytCOWKQiInB0IiIAiIgCIiAIiIAiIgCY9TQtiMjgMrAhlPQgjBEyRAOTcMLcJ1X936gn9FtJOjuPQEnelmPQjwz1l1kj2j4DTraG0+oXmRuh8VbwYHwInPeHcQv4dauh4i3NWxxpdafddfBHPg48/GWqVS6syrXo38US48wG56Dc/DqZv8AZijk01eTzFuZy3nzsXz9CJE664LVY53ArY7eI5TLBwlcUVDyrQf8oivsjzCrdm3IPXdl6LHSxRyPWxdeXZecjqVGx8JORKybWxaaT3KFxTg2pp0P6JWDa11p761B7qM+ScHzBmp2zIsuo0VFaWClQ1lZIXIACqudsnBzgTpEjeJ8B095BuqVmG4bGG+ok0a1nd+v7kM6N1aPp8Lr1KHr+NPoLu509o5Kq+Z6rSzczk57tWAyDjp8Je69Zl6GIK95WTg9QcBsfHrIHXdiAVIrtPt3pa/P7RIX7IPUSW7UXCparyCe7uXYePN7H/dPKsotK257SjNN324EnrdbXUvNYwUdBnqT5ADcn0Eoj6i39IYaRMV8odq7spgs2PYIBK5wTysJL2ndrrjlgCd+iL5L5bdT4zFwuohC7+/Yeds9QPsr8lx+Mz6lRSTRpUqTi076mppNcA5GoNdLjPKnNsV8WDMAD8BuJI8ldhqsIVu7sDKT0GQVJB+fWeraFb3gD8Rmebq1FbjG3I34DI/pIouzRNON4stcTDpGJRSepUZ+kzS+ZoiIgCIiAIiIAiIgCIiAIiIAiIgCaXF+FU6qpqdRWtlbdVYfQjyI8xN2IBynjPZziHD67F0ZOs0jIwFLn/aKQRj2W6Oo8uv5y7dle02l1NSrTaOdVUPU2UtUgYIKNhh0lgkFx7slpNWea6oCwe7chKWr8HXedObaSfA8UUtUTsSmf/z/ABLT/wC6a4Wp+61Kc5x5CxcH5nM+jjvFKwO94aLD4mi5SP8A5OWcnpcolObtneu1nC9YpPgBW/4oxAg9rtUw/VcJ1TerNSg/5nzALjIntVpe90lyDY8hKnyZfaH4iQba7jF21em0+nBHv22Gxh/IgwfrPi9i7r9+I6224eNNf6mn4YX2mHoSYPRTeuoqqYe7aFb5ABiPwx8zN4mQPAav0W+7hzbCv9bpvI6duqgnqUbI+GJPShUWV2NGlJSVxNfXJzIUHWwhB8zv9BmbEycLr7y/P2aRg+tpH9B+c9pRvI8rSyxJ9FwAPIT1ES8ZwiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIBB9qOAfpKo9b91qKSWouxnlbGCrD7SMNiPn1EiqdYwAXVIKLfEE5rJ80s6Eeh3lxni2pWGGAYeRAI+hnE6aluSU6jhsVRbzae70xDv42DeuoeLE9GbyUdfhLNoNGtSCtc4HUnqT1JJ8STvMtVSqMKoUeQAA+gnuIQUVoeTqOb1ERE7OBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQD//Z)

## Install

Using Python 3.6+

```sh
pip install barterdude
```

if you want Prometheus integration

```sh
pip install barterdude[prometheus] # or pip install barterdude[all]
```

## Usage

Build your consumer with this complete example:

```python
from barterdude import BarterDude
from barterdude.monitor import Monitor
from barterdude.hooks.healthcheck import Healthcheck
from barterdude.hooks.logging import Logging
from barterdude.hooks.metrics.prometheus import Prometheus
from asyncworker.rabbitmq.message import RabbitMQMessage

from my_project import MyHook # you can build your own hooks


# configure RabbitMQ
barterdude = BarterDude(
    hostname="localhost",
    username="guest",
    password="guest",
    prefetch=256,
)

# Prometheus labels for automatic metrics
labels = dict(
    app_name="my_app",
    team_name="my_team"
)
healthcheck = Healthcheck(barterdude) # automatic and customizable healthcheck

monitor = Monitor(
    healthcheck,
    Prometheus(barterdude, labels), # automatic and customizable Prometheus integration
    Logging() # automatic and customizable logging
)


@barterdude.consume_amqp(["queue1", "queue2"], monitor)
async def your_consumer(msg: RabbitMQMessage): # you receive only one message and we parallelize processing for you
    await barterdude.publish_amqp(
        exchange="my_exchange",
        data=msg.body
    )
    if msg.body == "fail":
        healthcheck.force_fail() # you can use your hooks inside consumer too
        msg.reject(requeue=True) # You can force to reject a message, exactly equal https://b2wdigital.github.io/async-worker/src/asyncworker/asyncworker.rabbitmq.html#asyncworker.rabbitmq.message.RabbitMQMessage

    if msg.body == "exception":
        raise Exception() # this will reject the message WITHOUT requeue to avoid processing loop
    
    # if everything is fine, than message automatically is accepted 

# register endpoint with a hook if you want
barterdude.add_endpoint(["http_endoint1", "http_endpoint2"], MyHook())


barterdude.run() # you will start consume and start a server on http://localhost:8080
# Change host and port with ASYNCWORKER_HTTP_HOST and ASYNCWORKER_HTTP_PORT env vars

```

### Build your own Hook

#### Base Hook (Simple One)

These hooks are called when message retreive, have success and fail.

```python
from barterdude.hooks import BaseHook
from asyncworker.rabbitmq.message import RabbitMQMessage

class MyCounterHook(HttpHook):
    _consume = _fail = _success = 0

    async def on_success(self, message: RabbitMQMessage):
        self._success += 1

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        self._fail += 1

    async def before_consume(self, message: RabbitMQMessage):
        self._consume += 1

```

#### Http Hook (Open Route)

These hooks can do everything simple hook does, but responding to a route.

```python
from barterdude.hooks import HttpHook
from asyncworker.rabbitmq.message import RabbitMQMessage

class MyCounterHttpHook(HttpHook):
    _consume = _fail = _success = 0

    async def __call__(self, req: web.Request):
        return web.json_response(dict(
            consumed=self._consume,
            success=self._success,
            fail=self._fail
        ))

    async def on_success(self, message: RabbitMQMessage):
        self._success += 1

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        self._fail += 1

    async def before_consume(self, message: RabbitMQMessage):
        self._consume += 1


```

### Testing

To test async consumers we recommend `asynctest` lib

```python
from asynctest import TestCase


class TestMain(TestCase):
    def test_should_pass(self):
        self.assertTrue(True)
```

We hope you enjoy! :wink:

## Contribute

For development and contributing, please follow [Contributing Guide](https://github.com/olxbr/BarterDude/blob/master/CONTRIBUTING.md) and **ALWAYS** respect the [Code of Conduct](https://github.com/olxbr/BarterDude/blob/master/CODE_OF_CONDUCT.md)