def SubHeader(text: str, text2: str = None) -> str:
    result = f'''
          <tr align="center" style="color: #79808E; font-size: 14px; {'border-bottom: 32px' if not text2 else ''} line-height: 16px;">
              <td>{text}</td>
          <tr>
    '''
    if text2:
        result += f'''
              <tr align="center" style="color: #79808E; font-size: 14px; line-height: 16px; border-bottom: 32px solid transparent;">
                  <td>{text2}</td>
              </tr>
        '''
    return result