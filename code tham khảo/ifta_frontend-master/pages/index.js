import { Button, Row, Col, Container } from "react-bootstrap";
import Head from "next/head";
import Image from "next/image";
import Link from "next/link";
import PresentationBanner from "../components/PresentationBanner";
import styles from "../styles/Home.module.css";

import fueling_icon from "../public/icons/Fueling.svg";
import miles_icon from "../public/icons/Miles.svg";
import reports_icon from "../public/icons/Reports.svg";
import youtube_icon from "../public/icons/Youtube.svg";
import ComplexBanner from "../components/ComplexBanner";

import phone_red_icon from "../public/icons/Phone Red.svg";
import analytic_red_icon from "../public/icons/Analytics Red.svg";
import reports_red_icon from "../public/icons/Reports Red.svg";
import SimpleBanner from "../components/SimpleBanner";

import signing_icon from "../public/icons/Signing Red.svg";
import data_icon from "../public/icons/Data Red.svg";
import tax_icon from "../public/icons/Tax Red.svg";
import file_icon from "../public/icons/File Red.svg";

import { useAuth } from "../context/AuthContext";
import { useEffect, useState } from "react"
import { useRouter } from 'next/router'


import ClientsTestimony from "../components/ClientsTestimony";



export default function Home() {

  const { auth, user, register } = useAuth();

  const router = useRouter()

  useEffect(() => {
    if (user != undefined) {
      router.push('/credentials/manage-account/account-info')
    }
  })


  return (
    <div className={styles.container}>
      <Head>
        <title>Spending-Webapp</title>
        <meta name="description" content="An app for personal or family finance management"/>
      </Head>

      <main className={styles.main}>

        <div className={styles.navbar_banner} >
          <h1 className={styles.navbar_h1}>
            Spending-Webapp
          </h1>
        </div>

        <PresentationBanner />

        <div className={styles.start_now_section}>
          <h2 className={styles.title_h2}>Profit of this App</h2>
          <p className={styles.start_section_p}>
            An affordable and easy-to-use form, help you calculate your incomes, spending, saving...
            By this way, you can tracking your spending and saving more for future life!
          </p>

          <div className={styles.start_now_button_div}>
            <Link href={'/credentials/register/create-account'}>
              <Button variant="danger" className={styles.start_now_button}>
                Register
              </Button>
            </Link>
          </div>
        </div>

        <div className={styles.features_section}>
          <Container>
            <Row className={styles.features_section_row}>
              {/* <Col
                xs={12}
                sm={12}
                md={12}
                lg={6}
                className={styles.features_section_col}
              > */}

                <div className='text-center'>
                  <h3 className={styles.title_h3}>Features</h3>

                  <p className={styles.features_section_p}>
                    Just enter your data manually and the App will take care the rest!
                    In additional, you can connect to your bank account to extract data automatically.
                  </p>
                </div>

                <Row className={styles.features_section_icon_row}>
                  <Col
                    xs={4}
                    sm={4}
                    md={4}
                    lg={4}
                    className={styles.features_section_icon_col}
                  >
                    <div className={styles.features_section_icon_col_wrapper}>
                      <Image
                        src={fueling_icon}
                        height={75}
                        width={75}
                        alt="Fueling Icon"
                      />
                      <p className={styles.features_section_icon_p}>Fueling</p>
                    </div>
                  </Col>

                  <Col
                    xs={4}
                    sm={4}
                    md={4}
                    lg={4}
                    className={styles.features_section_icon_col}
                  >
                    <div className={styles.features_section_icon_col_wrapper}>
                      <Image
                        src={miles_icon}
                        height={75}
                        width={75}
                        alt="Miles Icon"
                      />
                      <p className={styles.features_section_icon_p}>Miles</p>
                    </div>
                  </Col>

                  <Col
                    xs={4}
                    sm={4}
                    md={4}
                    lg={4}
                    className={styles.features_section_icon_col}
                  >
                    <div className={styles.features_section_icon_col_wrapper}>
                      <Image
                        src={reports_icon}
                        height={75}
                        width={75}
                        alt="Reports Icon"
                      />
                      <p className={styles.features_section_icon_p}>Reports</p>
                    </div>
                  </Col>
                </Row>
              {/* </Col> */}

              {/* Youtube Icon */}
              {/* <Col
                xs={12}
                sm={12}
                md={12}
                lg={6}
                className={styles.features_section_col}
              >
                <div className={styles.features_section_col_wrapper_div}>
                  <div className={styles.features_section_video_div}>
                    <div className={styles.features_section_video_icon_div}>
                      <Image
                        src={youtube_icon}
                        height={100}
                        width={100}
                        alt="Youtube Icon"
                        className={styles.video_icon}
                      />
                    </div>
                  </div>
                </div>
              </Col> */}
            </Row>
          </Container>
        </div>

        {/* <div className={styles.complex_banner}>
          <ComplexBanner />
        </div> */}

        <div className={styles.steps_section}>
          <Container className={styles.steps_section_container}>
            <Row className={styles.steps_section_icon_row}>
              <Col
                xs={12}
                sm={12}
                md={12}
                lg={4}
                className={styles.steps_section_icon_col}
              >
                <div className={styles.steps_section_icon_col_wrapper}>
                  <Image
                    src={phone_red_icon}
                    height={75}
                    width={75}
                    alt="Phone Red Icon"
                  />
                  <p className={styles.steps_section_icon_title}>
                    Fill on the App
                  </p>
                  <p className={styles.steps_section_icon_p}>
                    Easy-to-use by phone interface
                  </p>
                </div>
              </Col>

              <Col
                xs={12}
                sm={12}
                md={12}
                lg={4}
                className={styles.steps_section_icon_col}
              >
                <div className={styles.steps_section_icon_col_wrapper}>
                  <Image
                    src={analytic_red_icon}
                    height={75}
                    width={75}
                    alt="Analytics Red Icon"
                  />
                  <p className={styles.steps_section_icon_title}>Reports</p>
                  <p className={styles.steps_section_icon_p}>
                    Run reports by different time period
                  </p>
                </div>
              </Col>

              <Col
                xs={12}
                sm={12}
                md={12}
                lg={4}
                className={styles.steps_section_icon_col}
              >
                <div className={styles.steps_section_icon_col_wrapper}>
                  <Image
                    src={reports_red_icon}
                    height={75}
                    width={75}
                    alt="Report Red Icon"
                  />
                  <p className={styles.steps_section_icon_title}>Calculate</p>
                  <p className={styles.steps_section_icon_p}>
                    Calculate total and percentage of spending
                  </p>
                </div>
              </Col>
            </Row>
          </Container>
{/* 
          <div className={styles.step_section_button_div}>
            <Link href={'/credentials/register/create-account'}>
              <Button variant="danger" className={styles.step_section_button}>
                START NOW
              </Button>
            </Link>
          </div> */}
        </div>

        {/* <div className={styles.simple_banner}>
          <SimpleBanner />
          <div className={styles.simple_banner_features_div}>
            <Row className={styles.simple_banner_features_row}>
              <Col
                className={styles.simple_banner_features_col}
                xs={12}
                sm={12}
                md={12}
                lg={6}
              >
                <div className={styles.simple_banner_features_col_wrapper}>
                  <h3 className={styles.simple_banner_features_title}>
                    Need more?
                  </h3>

                  <p className={styles.simple_banner_features_p}>
                    Here you have some extra features to make complete the
                    simple IFTA Reports
                  </p>
                </div>
              </Col>

              <Col
                className={styles.simple_banner_features_col}
                xs={12}
                sm={12}
                md={12}
                lg={6}
              >
                <Row className={`${styles.simple_banner_features_extra_row} ${styles.simple_banner_features_extra_row_second_row}`}>
                  <Col
                    className={styles.simple_banner_features_extra_col}
                    xs={12}
                    sm={12}
                    md={12}
                    lg={6}
                  >
                    <div
                      className={
                        styles.simple_banner_features_extra_col_wrapper
                      }
                    >
                      <Image
                        src={signing_icon}
                        height={75}
                        width={75}
                        alt="Signing Icon"
                      />
                      <div
                        className={styles.simple_banner_features_extra_p_div}
                      >
                        <p className={styles.simple_banner_features_extra_p}>
                          Automatically update rates
                        </p>
                      </div>
                    </div>
                  </Col>

                  <Col
                    className={styles.simple_banner_features_extra_col}
                    xs={12}
                    sm={12}
                    md={12}
                    lg={6}
                  >
                    <div
                      className={
                        styles.simple_banner_features_extra_col_wrapper
                      }
                    >
                      <Image
                        src={tax_icon}
                        height={75}
                        width={75}
                        alt="Tax Icon"
                      />

                      <div
                        className={styles.simple_banner_features_extra_p_div}
                      >
                        <p className={styles.simple_banner_features_extra_p}>
                          Accurate tax calculations
                        </p>
                      </div>
                    </div>
                  </Col>

                  <Col
                    className={styles.simple_banner_features_extra_col}
                    xs={12}
                    sm={12}
                    md={12}
                    lg={6}
                  >
                    <div
                      className={
                        styles.simple_banner_features_extra_col_wrapper
                      }
                    >
                      <Image
                        src={data_icon}
                        height={75}
                        width={75}
                        alt="Data Icon"
                      />

                      <div
                        className={styles.simple_banner_features_extra_p_div}
                      >
                        <p className={styles.simple_banner_features_extra_p}>
                          Simple data upload entry
                        </p>
                      </div>
                    </div>
                  </Col>

                  <Col
                    className={styles.simple_banner_features_extra_col}
                    xs={12}
                    sm={12}
                    md={12}
                    lg={6}
                  >
                    <div
                      className={
                        styles.simple_banner_features_extra_col_wrapper
                      }
                    >
                      <Image
                        src={file_icon}
                        height={75}
                        width={75}
                        alt="File Icon"
                      />

                      <div
                        className={styles.simple_banner_features_extra_p_div}
                      >
                        <p className={styles.simple_banner_features_extra_p}>
                          Accounting Packages
                        </p>
                      </div>
                    </div>
                  </Col>
                </Row>
              </Col>
            </Row>
          </div>
        </div> */}

        {/* <div className={styles.clients_testimony_div}>
          <ClientsTestimony />
        </div> */}
      </main>
    </div>
  );
}
