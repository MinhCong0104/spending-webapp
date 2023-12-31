from datetime import datetime


def EmailTemplate(body: str) -> str:
    return f"""
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@100;200;300;400;500;600;700;800&display=swap" rel="stylesheet">
    <title></title>  
    </head>
    <body style="margin:0; padding:0; border-collapse: collapse; font-family: 'Roboto', sans-serif;">
        <center style="width: 100%; max-width: 600px; margin: auto; background: #F0F2F5;">
            <table width="100%"
                    border="0" 
                    cellspacing="0" 
                    cellpadding="0"
                    align="center" 
                    style="margin:0; padding:0; border-spacing: 0; border-collapse: collapse; width: 100%; max-width: 600px; height: 246px; background-size: cover;  
                    valign="top">
                
                <tr align="center" >
                <td height="100%" style="margin:0; padding:0; height: 100%;" >
                </td>
                </tr>
                <tr align="center">
                <td style="margin:0; padding:0;">
                </td>
                </tr>
            </table>
        
            <table width="100%"
                cellspacing="0" 
                cellpadding="0"
                align="center" 
                style="margin:0; padding:0; border-spacing: 0; border-collapse: collapse; width: 100%; width: 95%; max-width: 472px;  background: #ffffff; border: 1px solid #DEE3EC;" 
                valign="top">
                
                <tr>
                    <td style="padding: 42px">
                        <center>
                            <table
                                width="100%"
                                cellspacing="0" 
                                cellpadding="0"
                                align="center"
                                style="margin:0; padding:0; border-spacing: 0; border-collapse: collapse;">
                                    {body}

                                    <tr align="left" style="color: #626874; font-size: 12px; border-top: 32px solid transparent; color: #626874; border-left: 1px solid #18ABB6;">
                                        <td style="padding-left: 12px; line-height: 18px;">Sincerely,</td>
                                    </tr>
                                   <tr align="left" style="color: #626874; font-size: 12px; color: #4C505A; border-left: 1px solid #18ABB6;">
                                        <td style="padding-left: 12px; line-height: 18px; font-weight: 600">Verified Data Analytics</td>
                                    </tr>
                            </table>
                        </center>
                    </td>  
                </tr>
                
                <tr style="border-top: 1px solid #DEE3EC">
                    <tr align="center" style=" color: #9BA1AD; font-size: 12px;">
                        <td style="padding-top: 24px; padding-left: 24px; padding-right: 24px;">If you need help with service, don’t hesitate to send us an email: </td>
                    </tr>
                    <tr align="center" style="color: #9BA1AD; font-size: 12px; line-height: 20px;">
                        <td style="padding-bottom: 24px;"><a style="color: #18ABB6;" href="mailto:support@verifieddataanalytics.com">support@verifieddataanalytics.com</a></td>
                    </tr>
                </tr>
                
            </table>
            
            
            <table width="100%"
                cellspacing="0" 
                cellpadding="0"
                align="center" 
                style="margin:0; padding:0; border-spacing: 0; border-collapse: collapse; width: 100%; max-width: 600px;" 
                valign="top">
                    <tr>
                        <td align="center" style="border-top: 24px solid transparent;">
                            <a style="color: #4C505A; font-size: 12px; margin-right: 6px;" href="https://verifieddataanalytics.com/privacy-policy/">Privacy</a>
                            <a style="color: #4C505A; font-size: 12px; margin-right: 6px;" href="https://verifieddataanalytics.com/disclaimer/">Disclaimer</a>
                            <a style="color: #4C505A; font-size: 12px; margin-right: 6px;" href="https://verifieddataanalytics.com/terms-of-use/">Terms of use</a>
                        </td>
                    </tr>
                
                    <tr>
                        <td align="center" style="color: #9BA1AD; border-bottom: 24px solid transparent; border-top: 16px solid transparent; letter-spacing: 0.04em; text-transform: uppercase; font-size: 10px; font-weight: bold;" >
                            Copyright© {datetime.now().year} Verified Data Analytics
                        </td>
                    </tr>
            </table>
        </center>
    </body>
    """
