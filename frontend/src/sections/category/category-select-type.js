import * as React from 'react';
import {InputLabel, MenuItem, FormControl, Select} from '@mui/material';

export default function SelectVariants(props) {
  const [fieldValue, setFieldValue] = React.useState('');

  const handleChange = (event) => {
    setFieldValue(event.target.value);
  };
  console.log(fieldValue)

  return (
    <div>
      <FormControl 
        variant="filled"
        fullWidth
      >
        <InputLabel id="demo-simple-select-filled-label">{props.name}</InputLabel>
        <Select
          labelId="demo-simple-select-filled-label"
          id="demo-simple-select-filled"
          name={props.name}
          value={fieldValue}
          onChange={handleChange}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {props.valuesList.map((value) => (
            <MenuItem
              // key={name}
              value={value}
              // style={getStyles(name, personName, theme)}
            >
              {value}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
}