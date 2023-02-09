import asyncio
from aiohttp import web
import moment
import aiopg

async def main(request, get=None):
    config = {
        'database': 'd33egqep04b5pb',
        'user': 'ueg6lmies753k6',
        'password': 'p6c82a1628db28fa5e99accde47bf63cca55d8229409428b919f4346dfded3557',
        'host': 'ec2-54-155-156-83.eu-west-1.compute.amazonaws.com',
        'port': '5432',
        'ssl': {
            'rejectUnauthorized': False,
        }
    }
    next = request.rel_url.query.get('next', 0)
    subTime = request.rel_url.query.get('subTime', 1671375213)
    askedDate = moment.unix(subTime).format('yyyy-MM-DD HH:mm:ss')

    async with aiopg.create_pool(**config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"SELECT * FROM clients WHERE updated_at >= '{askedDate}' ORDER BY updated_at DESC LIMIT 500 OFFSET {next}")
                rows = await cur.fetchall()
                total = len(rows)
                if not total:
                    return web.Response(text='no data found')
                for row in rows:
                    if not row.email or row.email.includes('@highsociety.fr'):
                        row.emailId = row.uniq_email
                    else:
                        row.emailId = row.email

                bodyToSend = {
                    'LookUpName': 'Clients',
                    'datas': rows,
                    'events': [
                        {
                            'eventName': 'ERP_Contact_Created',
                            'eventTime': 'updated_at',
                            'insertId': ['ERP_Contact_Created_','$id']
                        },
                        {
                            'eventName': 'ERP_Contact_Updated',
                            'eventTime': 'updated_at',
                            'insertId': ['ERP_Contact_Updated_','$id','_','$updated_at']
                        }
                    ],
                    'Lookups': [
                        {
                            'value': 'salesman_id',
                            'lookup': 'Owners',
                            'id': 'idERP',
                            'key': 'Owners'
                        },
                        {
                            'value': 'id',
                            'lookup': 'Clients',
                            'id': 'idERP',
                            'key': 'Clients'
                        }
                    ],
                    'ids': {
                        'email' : 'emailId',
                        'idERP' : 'id'
                    },
                    'prefix': 'erp',
                    'properties': '',
                    'db': 'HighSociety_DEV'
                }

                if total == 500:
                    next += 500
                    bodyToSend['next'] = next
                return bodyToSend
