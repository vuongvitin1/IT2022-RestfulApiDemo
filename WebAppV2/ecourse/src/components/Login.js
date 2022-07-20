import React, { useContext, useState } from 'react'
import { Container, Form, Button, Alert } from 'react-bootstrap'
import { UserContext } from '../App'
import { Navigate } from 'react-router-dom'
import Api, {endpoints, authAxios} from '../configs/Api'
import cookies from 'react-cookies'

const Login = () => {
    const [username, setUsername] = useState()
    const [password, setPassword] = useState()
    const [errMsg, setErrMsg] = useState(null)
    const [user, dispatch] = useContext(UserContext)

    const login = async (event) => {
        event.preventDefault()

        // lay token
        try {
            const res = await Api.post(endpoints['login'], {
                'client_id': 'ZxSeDYfoRQgQ6FHwSv85H8TRfG6HlNAoUNe3njpG',
                'client_secret': '06pUsITeUpUkD6dcz2inC3RJ18X4UNYFM1PPPe633Tt5fYY3cK9Rftejgy5PmTv9IMXn75W4JjK3S27ELNOM1iTm4MVscBMWJze9ZsoQsptduNiH4o42TMOAujidx4p1',
                'username': username,
                'password': password,
                'grant_type': 'password'
            })
    
            if (res.status === 200) {
                cookies.save('access_token', res.data.access_token)
    
                // lay current user
                const user = await authAxios().get(endpoints['current_user'])
                cookies.save('current_user', user.data)
                dispatch({
                    "type": "login",
                    "payload": user.data
                })
            } 
        } catch (error) {
            console.info(error)
            setErrMsg('Username hoac password KHONG chinh xac!!!')
        }
    }

    if (user != null)
        return <Navigate to="/" />

    return (
        <Container>
            <h1 className="text-center text-danger">DANG NHAP</h1>

            {errMsg !== null && <Alert key='danger' variant='danger'>
                {errMsg}
            </Alert>}

            <Form onSubmit={login}>
                <Form.Group className="mb-3" controlId="formBasicEmail">
                    <Form.Label>Username</Form.Label>
                    <Form.Control type="test" value={username} onChange={evt => setUsername(evt.target.value)} placeholder="Nhap username..." />
                </Form.Group>

                <Form.Group className="mb-3" controlId="formBasicPassword">
                    <Form.Label>Password</Form.Label>
                    <Form.Control type="password" value={password} onChange={evt => setPassword(evt.target.value)} placeholder="Nhap password" />
                </Form.Group>
                <Button variant="primary" type="submit">
                    Dang nhap
                </Button>
            </Form>
        </Container>
    )
}

export default Login