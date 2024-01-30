import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/router';
import PropTypes from 'prop-types';
import { useAuthContext } from 'src/contexts/auth-context';
import Cookies from 'js-cookie';

export const AuthGuard = (props) => {
  const { children } = props;
  const router = useRouter();
  const { isAuthenticated } = useAuthContext();
  const ignore = useRef(false);
  const [checked, setChecked] = useState(false);

  // Only do authentication check on component mount.
  // This flow allows you to manually redirect th e user after sign-out, otherwise this will be
  // triggered and will automatically redirect to sign-in page.

  useEffect(() => {
    fetchProfile()
  }, [])

  async function fetchProfile() {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me`, {
        method: 'GET',
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + Cookies.get("token")
        }
      })
      if (res.ok) {
        // alert("Login success")
        router.push('/');
      } else {
        router.push("/auth/login")
      }
    } catch (err) {
      router.push("/auth/login")
    }
  }

  function logout() {
    localStorage.removeItem("token")
    router.push("/")
  }

  // If got here, it means that the redirect did not occur, and that tells us that the user is
  // authenticated / authorized.

  return children;
};

AuthGuard.propTypes = {
  children: PropTypes.node
};







// import { useRouter } from 'next/router'
// import { useState, useEffect } from 'react'
// import styles from '../styles/layout.module.css'

// export default function LayoutAuthenticated(props) {
//   const [profile, setProfile] = useState()
//   const router = useRouter()

//   useEffect(() => {
//     fetchProfile()
//   }, [])

//   async function fetchProfile() {
//     const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/test/profile`, {
//       headers: {
//         "Content-Type": "application/json",
//         "Authorization": "Bearer " + localStorage.getItem("token")
//       }
//     })
//     if (res.ok) {
//       const json = await res.json()
//       setProfile(json)
//     } else {
//       router.push("/signin")
//     }
//   }

//   function logout() {
//     localStorage.removeItem("token")
//     router.push("/")
//   }

//   return (
//     <div className={styles.layout}>
//       <div className={styles.nav}>
//         <p>Signed in as: {profile && profile.username}</p>
//         <p><button onClick={logout}>Log out</button></p>
//       </div>
//       {props.children}
//     </div>
//   )
// }